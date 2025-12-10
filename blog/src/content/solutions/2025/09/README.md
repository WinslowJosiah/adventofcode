---
year: 2025
day: 9
title: "Movie Theater"
slug: 2025/day/9
pub_date: "2025-12-10"
# concepts: []
---
## Part 1

The elves want help with interior decorating today. I don't have much of an eye
for style, but I'll do what I can!

Input parsing is super easy for this puzzle -- so easy, in fact, that one could
just use [eval()](https://docs.python.org/3/library/functions.html#eval) if one
were so inclined[^used-eval] (which I am not). But here, let's just write some
more safe and standard parsing code.

[^used-eval]: And [some were](https://reddit.com/comments/1phywvn/comment/nt6jiwb)!

```py title="2025\day09\solution.py"
from typing import cast

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        points = tuple(
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        )
        ...
```

We can write a simple function to take a pair of corners and calculate the area
of the containing rectangle -- the side lengths multiplied together. We then
want the maximum rectangle area over all pairs of input corners.

```py title="2025\day09\solution.py"
from itertools import combinations
...

def rectangle_area(corners: tuple[GridPoint, GridPoint]) -> int:
    (x1, y1), (x2, y2) = corners
    return (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1)

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        return max(
            rectangle_area(corners)
            for corners in combinations(points, 2)
        )
```

Suspiciously easy for being 3/4 of the way through Advent of Code. What could be
awaiting me in Part 2?

## Part 2

Looks like the piano of difficulty [has finally fallen on my head](https://reddit.com/comments/1pgnzgy).
Or at least, that's how I personally felt; it hasn't for others, especially
Python solvers who use external libraries such as [Shapely](https://shapely.readthedocs.io).

While I would usually defer to such a library for a personal script, I didn't
want to for Advent of Code; the core of Part 2 is checking whether an
axis-aligned rectangle is within an axis-aligned polygon, and surely there must
be a bulletproof way to check that myself... right?[^brute-force-point-in-polygon]

[^brute-force-point-in-polygon]: The only _absolutely_ bulletproof approach I
can think of would be to brute-force check that every single point within the
rectangle. While I'm sure that approach could somehow be optimized enough to be
viable for such a huge polygon, I wasn't going to be the one to do it.

I tried my absolute best to think about possible edge cases[^literally], and
looked at plenty of [examples](https://reddit.com/comments/1pi36pq). And from
this, I think I've found a set of conditions to check that are _good enough_ for
any example input I can think of (with a certain assumption). For a rectangle of
floor tiles to be within the input polygon:

[^literally]: _Literally_. The edges were very tricky to handle.

1. All corners of the rectangle must be within the polygon.
2. No edges of the polygon can extend to the inside of the rectangle. (Extending
to the _edge_ of the rectangle is okay.)
3. If you shrink the rectangle by one tile on all four sides, all corners of the
shrunken rectangle must be within the polygon.

I don't think this test ever gives a false positive, and the only case I can
think of where this test gives a false negative is where two adjacent parallel
edges of the polygon are inside the rectangle. But this case doesn't happen in
the sample input or the full puzzle input. So with that figured out, I could
finally breathe a sigh of relief and implement this check properly.

---

Now for the code. We can pretty easily make this a unified `solve` function. As
we calculate the areas of each new rectangle, we will manually keep track of
both answers -- one being the maximum rectangle area, and one being the maximum
rectangle area area that is _contained within the polygon_.

```py title="2025\day09\solution.py" /(rectangle_in_polygon)\\(/ ins={7-9,11-18,20}
class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        points = tuple(
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        )
        # HACK This solution only works if we enforce some assumptions -
        # some explicit in the prompt, some imposed by me.
        assert_polygon_is_valid(points)

        max_area, max_contained_area = 0, 0
        for corners in combinations(points, 2):
            area = rectangle_area(corners)
            if area > max_area:
                max_area = area
            if area > max_contained_area:
                if rectangle_in_polygon(corners, points):
                    max_contained_area = area

        return max_area, max_contained_area
```

:::caution
I take the opportunity here to enforce some assumptions about the polygon --
namely, that it's axis-aligned, and that no two parallel edges are adjacent. The
`assert_polygon_is_valid` function I wrote basically checks just that; you can
look at [my solution on GitHub](https://github.com/WinslowJosiah/adventofcode/blob/main/solutions/2025/day09/solution.py)
to see what the check entails, but rest assured that all of the assumptions I
make are true of the full puzzle input.
:::

We still need to implement the `rectangle_in_polygon` check, so let's do that
next. We'll implement each of the conditions I described one by one, starting
with this one:

1. All corners of the rectangle must be within the polygon.

We can worry about how to check if a point is within a polygon later. Once we
figure out how, checking all four corners of the rectangle is straightforward;
if not every corner is within the polygon, we can return `False`.

```py title="2025\day09\solution.py" "point_in_polygon"
def rectangle_in_polygon(
        corners: tuple[GridPoint, GridPoint],
        polygon: tuple[GridPoint, ...],
) -> bool:
    (rx1, ry1), (rx2, ry2) = corners
    # Sort rectangle X and Y values
    (rx1, rx2), (ry1, ry2) = sorted([rx1, rx2]), sorted([ry1, ry2])

    rectangle = ((rx1, ry1), (rx2, ry1), (rx2, ry2), (rx1, ry2))
    # Check if this rectangle's corners are all inside the polygon
    if not all(point_in_polygon(p, polygon) for p in rectangle):
        return False
    ...
```

(I also take the opportunity to sort the rectangle's X and Y values, as it saves
me some `min` and `max` calls later.)

The next condition is:

2. No edges of the polygon can extend to the inside of the rectangle. (Extending
to the _edge_ of the rectangle is okay.)

An "edge" of the polygon is basically a pair of connected points in its points
list (including the end connecting back to the start). Once we create a "padded"
list of polygon points to make it connected circularly, we can loop through each
pair of connected points with [`itertools.pairwise`](https://docs.python.org/3/library/itertools.html#itertools.pairwise).
Then we need to check if any part of the edge is strictly inside the rectangle;
if it is, we can return `False`.

```py title="2025\day09\solution.py" ins={1}
from itertools import pairwise

def rectangle_in_polygon(
        corners: tuple[GridPoint, GridPoint],
        polygon: tuple[GridPoint, ...],
) -> bool:
    ...
    # HACK Here, we check that no edge of the polygon goes inside the
    # rectangle. This is technically incorrect - two adjacent, parallel
    # polygon edges would make the check fail even if no rectangle point
    # is "outside" - but that edge case doesn't happen in our input.
    padded_polygon = [*polygon, polygon[0]]
    for (px1, py1), (px2, py2) in pairwise(padded_polygon):
        # Sort polygon X and Y values
        (px1, px2), (py1, py2) = sorted([px1, px2]), sorted([py1, py2])
        # Check if this polygon edge overlaps the rectangle's interior
        # (which happens if its X ranges and Y ranges intersect)
        if px1 < rx2 and rx1 < px2 and py1 < ry2 and ry1 < py2:
            return False
    ...
```

Finally, the last condition is:

3. If you shrink the rectangle by one tile on all four sides, all corners of the
shrunken rectangle must be within the polygon.

This is also very straightforward, and works similarly to our first condition.
We can compile the positions of each shrunken "inner corner" by adding 1 to the
top/left coordinates, and subtracting 1 from the bottom/right coordinates; if
not every "inner corner" is within the polygon, we can return `False`.

```py title="2025\day09\solution.py" "point_in_polygon"
def rectangle_in_polygon(
        corners: tuple[GridPoint, GridPoint],
        polygon: tuple[GridPoint, ...],
) -> bool:
    ...
    # HACK The preceding tests will incorrectly say the empty inside of
    # a horseshoe-like shape is "inside" the polygon. This shape occurs
    # in our input, but doesn't affect our answer because it's so thin;
    # nevertheless, to detect it, we also check the rectangle's "inner
    # corners" (if it is big enough to have any).
    if rx2 - rx1 > 1 and ry2 - ry1 > 1:
        inner_corners = (
            (rx1 + 1, ry1 + 1),
            (rx2 - 1, ry1 + 1),
            (rx2 - 1, ry2 - 1),
            (rx1 + 1, ry2 - 1),
        )
        if not all(point_in_polygon(p, polygon) for p in inner_corners):
            return False

    return True
```

And if none of our tests has ruled out the rectangle being within the polygon,
we can return `True` at the very end of the function.

Our work here is almost done. Again, all we'd need to do from here is write the
`point_in_polygon` function. For this, we'll use an algorithm called the
[even-odd rule](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule).[^2023-day-10]

[^2023-day-10]: I learned about the even-odd rule when I solved [2023 Day 10](/solutions/2023/day/10),
but decided not to use it in my revised solution. If only that me could see me
now...

The **even-odd rule** is a way to check whether or not a certain point is within
a polygon. Imagine that you draw some ray starting at a certain point, and you
extend it outwards infinitely. Each time that ray crosses an edge, it switches
from being outside to inside to outside to inside, and so on; thus, every two
edge crossings, the "insideness" stays the same. This leads to two possible
cases:

- If the ray does an _even_ number of edge crossings before reaching the
outside, the original point was _outside_.
- If the ray does an _odd_ number of edge crossings before reaching the outside,
the original point was _inside_.

The only case that would difficult to check for with this algorithm is a point
that's exactly on the boundary. But that's okay; we can just explicity check for
that condition first, and return `True` if our point lies within the bounds of
the edge coordinates.[^point-on-boundary]

[^point-on-boundary]: What the code actually checks is if our point is within
a _rectangle_ defined by the minimum and maximum X and Y values of the edge.
This is okay, because we know the edges are all axis-aligned, meaning the edge
"rectangle" is only one tile high or wide.

```py title="2025\day09\solution.py"
from functools import cache
...

@cache
def point_in_polygon(point: GridPoint, polygon: tuple[GridPoint, ...]) -> bool:
    x, y = point
    padded_polygon = [*polygon, polygon[0]]

    # Check if point is exactly on an edge (which counts as inside)
    for (x1, y1), (x2, y2) in pairwise(padded_polygon):
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return True
    ...
```

Now for the even-odd rule itself. We can choose any direction to extend the ray,
so I've arbitrarily decided to extend it to the right. Counting the number of
rightward edge crossings amounts to iterating through every edge, and tallying
it if it's a vertical edge, its X position is to the right, and its Y range
includes the Y of the ray/point. Then we return whether the number of crossings
is odd.

```py title="2025\day09\solution.py"
from functools import cache
...

@cache
def point_in_polygon(point: GridPoint, polygon: tuple[GridPoint, ...]) -> bool:
    ...
    # NOTE Consider a horizontal ray going rightward from the point, and
    # count the edges it crosses; if it's even, the point is outside,
    # and if it's odd, the point is inside. This is the "even-odd rule".
    crossings = 0
    for (x1, y1), (x2, y2) in pairwise(padded_polygon):
        # Horizontal edges will never be crossed
        if y1 == y2:
            continue
        # This vertical edge is crossed if its X is to the right and our
        # horizontal ray is within its Y range
        if x < x1 and min(y1, y2) < y <= max(y1, y2):
            crossings += 1

    # An odd number of crossings means we are inside
    return crossings % 2 == 1
```

(Note that I've slapped the [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache)
decorator on the function to speed up repeated calls. That's needed badly for a
task like this.)

I wasn't very happy about the fact that I couldn't come up with a solution that
works in absolutely every case, but I got as close as I could manage to get. To
me, that's good enough.
