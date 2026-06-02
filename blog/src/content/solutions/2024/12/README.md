---
year: 2024
day: 12
title: "Garden Groups"
slug: 2024/day/12
pub_date: "2026-06-02"
# concepts: []
---
## Part 1

Another day, another grid puzzle. In fact, this is our _fifth_ (!) grid puzzle
this year; please revisit my solutions to [Day 4](/solutions/2024/day/4), [Day 6](/solutions/2024/day/6),
[Day 8](/solutions/2024/day/8), and [Day 10](/solutions/2024/day/10) if you want
a refresher on how I handle grids.

Once we _have_ our grid, though, we'll want to be able to iterate through all of
the interconnected regions of flowers. Something like the [flood fill](https://en.wikipedia.org/wiki/Flood_fill)
algorithm should come to mind; in effect, we can gather the points of a region
by "flood filling" from an arbitrary point, and we can do this for every point
to get every region.

```py title="2024\day12\solution.py"
from collections.abc import Iterator

def iter_regions(grid: Grid[str]) -> Iterator[set[GridPoint]]:
    seen: set[GridPoint] = set()
    for point in grid:
        if point in seen:
            continue

        region: set[GridPoint] = set()
        # Regions will be determined using flood fill
        queue = [point]
        while queue:
            current = queue.pop()
            if current in region:
                continue

            region.add(current)
            queue.extend(
                n for n in neighbors(current, num_directions=4)
                if grid.get(n) == grid[current]
            )

        seen |= region
        yield region
```

The implementation above is mostly straightforward, except we have to do a bit
of bookkeeping to avoid "flood filling" from any point twice.[^destructive-bookkeeping]
The `seen` set will contain every point seen by a flood fill, and the `|=`
operator is used to add each region's points to that `seen` set as they're
found.

[^destructive-bookkeeping]: If memory usage were more of a concern, we _could_
avoid revisiting any points of a region by _removing_ those points from the grid
when we find them. But our memory usage isn't really that bad for our purposes,
and there's otherwise not much benefit to this destructive bookkeeping.

Now for each region, we need to calculate a price based on its perimeter and
area. The area is easy; that's just the length of the set of points making up
the region. But how do we calculate the perimeter? Let's look in detail at the
sample input:

```text
AAAA
BBCD
BBCC
EEEC

+-+-+-+-+
|A A A A|
+-+-+-+-+
|B B|C|D|
+   + +-+
|B B|C C|
+-+-+-+ |
|E E E|C|
+-+-+-+-+
```

That one-tile `D` region is the simplest to calculate the perimeter of: it has 4
sides, none of which border a matching tile, so its perimeter is **4**. In fact,
every single individual tile _technically_ has a perimeter of 4... except we
only want to count the _external_ borders of each tile, and not the _internal_
borders between matching neighbor tiles. For instance, in the long horizontal
`E` region:

- The outermost `E`s both contribute **3** to the region's perimeter -- **3**
external borders, and 1 internal border shared with the middle `E`.
- The middle `E` contributes **2** to the region's perimeter -- **2** external
borders on top and bottom, and 2 internal borders shared with the outermost
`E`s.
- Thus, the perimeter of the `E` region is 3 + 2 + 3, or **8**.

So to calculate a region's perimeter, we can loop through all its points, add 4
for that point, and subtract the number of matching neighbors of that point.
This leaves us with a count of _external_ borders -- exactly the perimeter we
wanted -- which we can use to calculate our final answer.

```py title="2024\day12\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        price = 0
        for region in iter_regions(grid):
            perimeter = 0
            for point in region:
                # Count all non-matching neighbors of this point
                num_matching_neighbors = len(
                    [
                        n for n in neighbors(point, num_directions=4)
                        if grid.get(n) == grid[point]
                    ]
                )
                perimeter += 4 - num_matching_neighbors

            price += perimeter * len(region)

        return price
```

Before we move on to Part 2, however, I'd like to point out that we've got a bit
of repeated logic: both the `iter_regions` function and our perimeter
calculation depend on checking the matching neighbors of a point in the grid. If
we want to avoid repeating ourselves,[^dry-wet-and-damp] we can factor out this
logic into a `matching_neighbors` function like so:

[^dry-wet-and-damp]: The commonly-promoted "[DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)"
principle (**D**on't **R**epeat **Y**ourself) would tell us that it would be a
good idea to factor out repeated logic. This is in contrast to the
creatively-named "WET" principle (**W**rite **E**verything **T**wice). But in my
opinion, the best approach is somewhere in between those two extremes... in
other words, the "DAMP" principle (**D**on't **A**bstract **M**ethods
**P**rematurely).

```py title="2024\day12\solution.py" del={15-18,30-36} ins={19,37} /(matching_neighbors)\\(/
def matching_neighbors(
        grid: Grid[str],
        point: GridPoint,
) -> Iterator[GridPoint]:
    for n in neighbors(point, num_directions=4):
        if grid.get(n) == grid[point]:
            yield n

def iter_regions(grid: Grid[str]) -> Iterator[set[GridPoint]]:
    ...
    for point in grid:
        ...
        while queue:
            ...
            queue.extend(
                n for n in neighbors(current, num_directions=4)
                if grid.get(n) == grid[current]
            )
            queue.extend(matching_neighbors(grid, current))
        ...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        for region in iter_regions(grid):
            ...
            for point in region:
                ...
                # Count all non-matching neighbors of this point
                num_matching_neighbors = len(
                    [
                        n for n in neighbors(point, num_directions=4)
                        if grid.get(n) == grid[point]
                    ]
                )
                perimeter += 4 - num_matching_neighbors
                perimeter += 4 - len(list(matching_neighbors(grid, point)))
            ...
        ...
```

I'd say this abstraction is a good idea here; it makes the relevant portions
more [readable](https://pep20.org/#readability).

## Part 2

We were a bit lucky that we could calculate each region's perimeter one tile at
a time; as far as I know, we can't count the number of sides this way (without
some rather complex bookkeeping). But luckily, any polygon has exactly as many
sides as corners -- and we _can_ count the number of _corners_ one tile at a
time. So let's turn this into a unified `solve` function, and mentally prepare
to count each region's corners.

```py title="2024\day12\solution.py" ins={8-9,19} {15-16} ins="solve" ins="tuple[int, int]" ins=/(perimeter_)price(, side_price)/ ins=", 0" ins=", num_corners" ins=/(perimeter_)price \\+=/
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        perimeter_price, side_price = 0, 0
        for region in iter_regions(grid):
            # NOTE Each region has exactly as many sides as corners.
            # Thus, we can simply count the corners to count the sides.
            perimeter, num_corners = 0, 0
            for point in region:
                # Count all non-matching neighbors of this point
                perimeter += 4 - len(list(matching_neighbors(grid, point)))

                # TODO Add count-each-corner code
                num_corners += 0

            perimeter_price += perimeter * len(region)
            side_price += num_corners * len(region)

        return perimeter_price, side_price
```

Just like before, the absolute simplest case for counting corners is a region
with only a single tile; obviously, it has 4 corners. Extending that to a
general corner-counting strategy is tricky, but similarly to Part 1, it will
involve looking at the tiles _around_ each individual tile's corners and
checking which corners are external to the region.[^not-external-angles] Let's
see what corner-counting criteria we can come up with.

[^not-external-angles]: When I say this, I'm not referring to
[internal vs. external angles](https://en.wikipedia.org/wiki/Internal_and_external_angles).
By "external" corners, I mean tile corners that are properly counted as corners
of the region, because they're on the outside; this is analogous to how I
counted "external" borders in Part 1 as tile borders on the outside of their
region.

In my estimation, there are two types of corners we could be dealing with, which
I will call "outer corners" and "inner corners". To show you what I mean, here's
an ASCII-art illustration of both kinds of corner.

```text
outer   inner
          +-+
 X B     B#A|
  ##+   +## +
 B#A|   |A A|
  +-+   +-+-+
```

Here, we're looking at the top-left corner of the `A` tile on the bottom-right.
And here's what I want you to notice:

- An outer corner is created when the two orthogonal neighbors are outside the
region (I've marked those tiles with `B`).
    - It doesn't matter what the diagonal neighbor is, so I've marked that tile
    with an `X`.
- An inner corner is created when the two orthogonal neighbors are inside the
region, but the diagonal neighbor is _not_.

In fact, the contents of the three tiles surrounding each corner are enough to
determine whether a corner is one of these two types -- and thus, whether it is
a corner of the region. This way of categorizing corners does seem to make sense
when looking at all 8 possible cases of what those tiles could be (where `A` is
inside the region and `B` is outside):

```text
is an outer corner
        +-+  
 B B    |A|B 
  ##+   +-##+
 B#A|    B#A|
  +-+     +-+

is an inner corner
  +-+
 B#A|
+## +
|A A|
+-+-+

is NOT a corner
+-+-+             +-+   +-+-+   +-+  
|A A|    B B     B|A|   |A A|   |A|B 
+ # +   +-#-+     # +   +-# +   + #-+
|A A|   |A A|    B|A|    B|A|   |A A|
+-+-+   +-+-+     +-+     +-+   +-+-+
```

:::attention
Those last two "not a corner" cases sure _look_ like they're corners... and if I
were manually counting corners as a human, I would agree.

But remember, we're looking at the top-left corner of the bottom-right `A` tile;
those two cases would count as inner corners in relation to some _different_
tile, and we don't want to count the same point as a corner more than once! This
is subtle, but important to the correctness of our counting.
:::

Now all we have to do is turn our corner criteria into code! To get the three
tiles surrounding each potential corner, I'm using a convenience function from
my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
called `offsets`; from there, it's a matter of translating our corner cases (no
pun intended) into conditions, and incrementing our corner count if one of those
conditions is true.

```py title="2024\day12\solution.py" ins={10-25}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        for region in iter_regions(grid):
            ...
            for point in region:
                ...
                row, col = point
                # For each possible offset of a corner
                for dr, dc in offsets(num_directions=4, diagonals=True):
                    has_row_neighbor = (row + dr, col) in region
                    has_col_neighbor = (row, col + dc) in region
                    has_diagonal_neighbor = (row + dr, col + dc) in region

                    # Is this an outer corner?
                    if not has_row_neighbor and not has_col_neighbor:
                        num_corners += 1
                    # Is this an inner corner?
                    if (
                        has_row_neighbor and has_col_neighbor
                        and not has_diagonal_neighbor
                    ):
                        num_corners += 1
            ...
        ...
```

I don't think it would've been this easy to count each region's sides directly.
This just goes to show that it sometimes pays to ask a _different_ question with
the same answer, because it may make the answering process easier!
