---
year: 2024
day: 10
title: "Hoof It"
slug: 2024/day/10
pub_date: "2026-05-28"
# concepts: []
---
## Part 1

Another day, another grid puzzle. After [Day 4](/solutions/2024/day/4), [Day 6](/solutions/2024/day/6),
and [Day 8](/solutions/2024/day/8), this is the _fourth_ one we've seen so far
this year; check out those previous writeups to remind yourself how I've been
using my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py).

On previous days this year, I was able to use my `parse_grid` function to
convert the puzzle input to a grid of string characters. Let's take a look at
the implementation of this function:

```py title="utils\grids.py"
from collections.abc import Callable, Iterable

type GridPoint = tuple[int, int]
type Grid[Item] = dict[GridPoint, Item]

def parse_grid[Item](
        raw_grid: list[str],
        item_factory: Callable[[str], Item] = str,
        *,
        ignore_chars: Iterable[str] = "",
) -> Grid[Item]:
    result: Grid[Item] = {}
    ignore = set(ignore_chars)
    for row, line in enumerate(raw_grid):
        for col, char in enumerate(line):
            if char in ignore:
                continue
            result[row, col] = item_factory(char)
    return result
```

It's a pretty simple loop, though it does a bit more than I've been using it for
so far.

- The optional `ignore_chars` argument allows certain characters of the grid to
be ignored and excluded from the resulting grid. For testing the sample inputs,
I'll want to ignore the `.` characters, as they can't be part of any trail.
- Each item passes through `item_factory` before being placed in the grid --
similar to how [`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
and its `default_factory` argument works. By default, this "factory function" is
`str`, meaning each item is converted to a string.[^parse-grid-default-factory]
I'll want to use `int` as the "factory function" to convert each digit in the
grid to a number.

[^parse-grid-default-factory]: Because each character will already be a string,
I could've technically made the "factory function" a no-op (i.e. do-nothing)
function. But having it be `str` makes this fact more [explicit](https://pep20.org/#explicit).

So for this puzzle, the first thing I'll do is make use of those optional
arguments to `parse_grid`, so the grid will be in a useful format to us.

```py title="2024\day10\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, int, ignore_chars=".")
        ...
```

Now that we have a grid of numbers, we'll use it to do some pathfinding. We'll
want to count how many unique `9`s we can reach from each `0`, which we can do
with a simple form of search. Given a valid trailhead, we can put it in a queue[^queue-or-stack]
and repeat the following until the queue is empty:

[^queue-or-stack]: Technically I'll be putting it into a [stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)),
not a [queue](https://en.wikipedia.org/wiki/Queue_(abstract_data_type)). But in
this case, it doesn't matter what order we process the paths we walk down, so it
doesn't matter what data structure we use.

1. Pop a grid point from the queue.
2. If this point is a valid endpoint, add it to a endpoint set and continue. (We
want it to be a `set` because we're counting _unique_ endpoints.)
3. Add all valid _next_ points from here to the queue.[^retracing-steps]

[^retracing-steps]: In other contexts, it would also make sense to ensure we
don't retrace our steps and revisit any points we've already visited. But in
_this_ context, each path can only go in a single direction, so we won't be
retracing our steps.

```py title="2024\day10\solution.py" {"1":8} {"2":10-12} {"3":14-17}
def get_trailhead_ends(
        grid: Grid[int],
        trailhead: GridPoint,
) -> set[GridPoint]:
    queue = [trailhead]
    ends: set[GridPoint] = set()
    while queue:
        point = queue.pop()
        # If our point has height 9, it is the end of a trail
        if (height := grid[point]) == 9:
            ends.add(point)
            continue
        # Continue walking along points that are exactly 1 higher
        queue.extend(
            n for n in neighbors(point, num_directions=4)
            if grid.get(n) == height + 1
        )
    return ends
```

To walk to every possible next point in step 3, I use a `neighbors` helper
function to get each neighboring point, and filter those to only the neighbors
that are exactly 1 higher than the current point. My implementation of
`neighbors` is somewhat long (because it handles more use cases than this), so
read the source code for my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
if you want to see how it works.

Finally, we'll want to loop through each trailhead in the grid -- the locations
with a height of 0 -- and add up their scores -- the number of unique endpoints
we can reach starting from the trailhead. This leads to a pretty straightforward
final answer.

```py title="2024\day10\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        total_scores = 0
        for point, height in grid.items():
            # Only count ends from trailheads, i.e. points with height 0
            if height != 0:
                continue
            ends = get_trailhead_ends(grid, point)
            total_scores += len(ends)

        return total_scores
```

## Part 2

For some Advent of Code puzzles, it's easy to accidentally solve Part 2 _before_
you solve Part 1. And if we had made a slightly different choice of data
structure during Part 1, perhaps that would've happened to us.

Recall that in the `get_trailhead_ends` function from before, we collect the
unique trailhead endpoints into a `set` to count the unique ones. But what
would've happened if we had collected them into a `list` instead? Then an
endpoint would be added to the list _every_ time it was reached, instead of only
the _first_ time.

To see this, let's change the endpoint `set` to an endpoint `list`, and see what
this list looks like.

```py title="2024\day10\solution.py" ins="list" ins="[]" ins="append"
def get_trailhead_ends(
        grid: Grid[int],
        trailhead: GridPoint,
) -> list[GridPoint]:
    queue = [trailhead]
    ends: list[GridPoint] = []
    while queue:
        point = queue.pop()
        # If our point has height 9, it is the end of a trail
        if (height := grid[point]) == 9:
            ends.append(point)
            continue
        # Continue walking along points that are exactly 1 higher
        queue.extend(
            n for n in neighbors(point, num_directions=4)
            if grid.get(n) == height + 1
        )
    return ends
```

Let's use this test case from the original prompt as an example. It consists of
a single trailhead with a score of **4** and a rating of **13**.

```text
..90..9
...1.98
...2..7
6543456
765.987
876....
987....
```

And if we print that trailhead's list of endpoints, we see why its score and
rating are what they are:

```py
[
    (4, 4),
    (1, 5),
    (0, 6),
    (6, 0), (6, 0), (6, 0), (6, 0), (6, 0), (6, 0), (6, 0), (6, 0), (6, 0), (6, 0)
]
```

There are **4** _unique_ values -- `(4, 4)`, `(1, 5)`, `(0, 6)`, and `(6, 0)` --
and there are **13** values overall. Each value is the location of an endpoint,
and each endpoint is included as many times as it is reached during the search.
This reflects the fact that some endpoints can be reached in multiple ways; for
example, `(4, 4)`, `(1, 5)`, and `(0, 6)` (the `9`s on the right-hand side) can
each only be reached with _one_ trail, and `(6, 0)` (the `9` on the lower left
corner) can be reached with _multiple_ trails.

This means that the length of the endpoint list is the trailhead's _rating_, and
the amount of _unique_ items in this list is its _score_. So once we have our
`ends` list, we can count the unique endpoints with `len(set(ends))`, and count
the endpoints overall with `len(ends)`.

```py title="2024\day10\solution.py" ins="solve" ins="tuple[int, int]" ins=", total_ratings" ins=", 0" ins=/(set\\()ends(\\))/ ins={14}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, int, ignore_chars=".")

        total_scores, total_ratings = 0, 0
        for point, height in grid.items():
            # Only count ends from trailheads, i.e. points with height 0
            if height != 0:
                continue
            ends = get_trailhead_ends(grid, point)
            total_scores += len(set(ends))
            total_ratings += len(ends)

        return total_scores, total_ratings
```

The difference between Parts 1 and 2 is a bit subtle, and I can easily imagine
that tripping someone up. But we made it to the end of the trail!
