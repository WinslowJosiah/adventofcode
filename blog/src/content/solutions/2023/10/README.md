---
year: 2023
day: 10
title: "Pipe Maze"
slug: 2023/day/10
pub_date: "2025-10-20"
# concepts: []
---
## Part 1

Here it is: the _first_ grid puzzle I'd ever encountered in Advent of Code! I
had fun coming up with my [initial solution](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2023/day10/__init__.py),
which had a neat approach to Part 2;[^initial-solution] instead of that,
however, I'll be explaining a different approach.

[^initial-solution]: My initial Part 2 solution used the ["even-odd rule"](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule)
and `re.split` on each text line to count the tiles inside the pipe loop. But I
had to modify the input in-place to get my approach to work, which made it a bit
clunky because strings are immutable.

    The even-odd rule is neat, though; perhaps I'll find some excuse to talk
    about it here.

But first, I want to talk about how I handle AoC grid puzzles, using a
[`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
I wrote (which I modified from [David Brownman's `graphs` module](https://github.com/xavdid/advent-of-code/blob/main/solutions/utils/graphs.py)
from his solution repo). Basically, grids are parsed into dicts that map
`(row, column)` location tuples to grid items. This doesn't involve a lot of
code; in fact, here is the entire `parse_grid` function:

```py title="utils\grids.py"
from collections.abc import Callable, Iterable

# NOTE This type-alias syntax was added in Python 3.12.
type GridPoint = tuple[int, int]
type Grid[Item] = dict[GridPoint, Item]

# NOTE This generic-function syntax was also added in Python 3.12.
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

This function can be used to quickly parse a grid in certain useful ways:

- `parse_grid(self.input)`: grid with string characters at each grid point
- `parse_grid(self.input, int)`: grid with `int`s at each grid point (each
character is passed to `int`)
- `parse_grid(self.input, str, ignore_chars=".#")`: grid with string characters
at each grid point, _without_ any `.` or `#` characters

My `grids` module also defines other common grid-related functions, which I'll
explain as they come up.

---

We're looking for a loop of pipe tiles in a grid. First, let's parse the grid,
ignoring any non-pipe tiles; we can easily use `next` with a generator
expression to find the starting point.

```py title="2023\day10\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars=".")
        start = next(k for k, v in grid.items() if v == "S")
        ...
```

To traverse the loop, we'll need to know which directions the pipes connect to.
My `grids` module includes a `Direction` class that makes some direction-related
operations easier:

```py title="utils\grids.py"
from enum import IntEnum

class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @property
    def offset(self) -> GridPoint:
        return _ROW_COLUMN_OFFSETS[self]

_ROW_COLUMN_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}
```

As I've defined it, each direction has an `offset` property, which is what you'd
need to add to the row/column of a grid point to move it in that direction. I
also define a function to do this addition:

```py title="utils\grids.py"
def add_points(a: GridPoint, b: GridPoint) -> GridPoint:
    return a[0] + b[0], a[1] + b[1]
```

This can be used to write a function that gets both possible moves that can be
made from any pipe tile. We will get the directions you can travel from a pipe
tile from a lookup table.

```py title="2023\day10\solution.py"
PIPES = {
    "|": (Direction.UP, Direction.DOWN),
    "-": (Direction.RIGHT, Direction.LEFT),
    "L": (Direction.UP, Direction.RIGHT),
    "J": (Direction.UP, Direction.LEFT),
    "7": (Direction.DOWN, Direction.LEFT),
    "F": (Direction.RIGHT, Direction.DOWN),
}

def possible_moves(current: GridPoint, ch: str) -> tuple[GridPoint, GridPoint]:
    result = tuple(add_points(current, d.offset) for d in PIPES[ch])
    assert len(result) == 2
    return result
```

There's just one problem: how do we know which ways the `S` tile connects?
According to the prompt, it (like every other pipe tile) has two pipes connected
to it, and it connects back to those two pipes. So we can look at each of the
tiles that neighbor the `S`, and check whether they connect back to the `S`.

My `grids` module has a `neighbors` function for looping through the neighbors
of a grid point. I won't paste it here because it's somewhat long; all you need
to know is that `neighbors(start, num_directions=4)` yields the neighbors of
`start` going up, down, left, and right.

```py title="2023\day10\solution.py"
def get_moves_from_start(grid: Grid[str], start: GridPoint) -> list[GridPoint]:
    moves: list[GridPoint] = []
    for neighbor in neighbors(start, num_directions=4):
        if neighbor not in grid:
            continue
        if start in possible_moves(neighbor, grid[neighbor]):
            moves.append(neighbor)
    assert len(moves) == 2, "didn't find two moves possible from start"
    return moves
```

:::note
Thanks to the fact that our grids are `dict`s, we can check if a point is in the
grid by literally checking whether `point in grid` is true! This is also why I
chose to ignore non-pipe tiles.
:::

Now that _all_ of that's out of the way, we can solve Part 1.

We need the number of steps to the farthest point from the starting position;
that's going to be at the exact halfway point, since that's as far as we can go
without getting closer to the start again. We'll walk along the pipe loop until
we get back to the start, collecting the points we visit into a list as we go.
Each time, the next tile we visit will simply be the one we _didn't_ just visit.

```py title="2023\day10\solution.py" ins={8-18}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars=".")
        start = next(k for k, v in grid.items() if v == "S")

        points = [start]
        current = get_moves_from_start(grid, start)[0]
        while current != start:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])
            current = a if b == last else b

        # The farthest point from the start is the halfway point of the
        # loop
        return len(points) // 2
```

## Part 2

How many tiles are enclosed by the pipe loop? Well, the pipe loop is basically a
polygon, and we know the coordinates of its vertices. From this information, we
can use the [shoelace formula](https://en.wikipedia.org/wiki/Shoelace_formula)
to calculate the area of the polygon. How convenient!

If $(x_n, y_n)$ are the coordinates of the $n$th vertex of a polygon (going
clockwise or counterclockwise), then the area $A$ is given by:

$$
A = \frac{1}{2} \left| \sum_{i=1}^{n} (x_i y_{i+1} - x_{i+1} y_i) \right|
$$

(Note that the list of vertices are treated as circular; after the last vertex
($i = n$), the next vertex is the first one ($i + 1 = 1$).)

We can easily write a function that uses this formula, which I also put in my
`grids` module.

```py title="utils\grids.py"
from itertools import pairwise

def interior_area(points: list[GridPoint]) -> float:
    # NOTE The "shoelace formula" requires a circular list of vertices.
    padded_points = [*points, points[0]]
    return abs(sum(
        row1 * col2 - row2 * col1
        for (row1, col1), (row2, col2) in pairwise(padded_points)
    )) / 2
```

But we must be careful! Strictly speaking, we don't want the _area_ within the
pipe loop; we want the number of _grid points_ within the pipe loop. Luckily,
there's a formula that relates the area of a polygon to the number of grid
points inside of it, given by [Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem).
Again, how convenient!

If $i$ is the number of grid points _inside_ of a polygon, and $b$ is the number
of grid points on its _boundary_, then its area $A$ is given by:

$$
A = i + \frac{b}{2} - 1
$$

Solving for $i$ gives us $i = A - \frac{b}{2} + 1$. We know the area of the pipe
loop, and we know the number of boundary points (the number of points along the
loop), so we can simply plug these numbers in!

```py title="2023\day10\solution.py" ins="solve" ins="tuple[int, int]" ins="farthest_loop_distance =" ins={20-26}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, ignore_chars=".")
        start = next(k for k, v in grid.items() if v == "S")

        points = [start]
        current = get_moves_from_start(grid, start)[0]
        while current != start:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])
            current = a if b == last else b

        # The farthest point from the start is the halfway point of the
        # loop
        farthest_loop_distance = len(points) // 2

        area = interior_area(points)
        # NOTE Pick's theorem relates the area, number of interior grid
        # points, and number of boundary grid points of a simple lattice
        # polygon. This formula follows from simple algebra.
        num_interior_points = int(area - len(points) / 2 + 1)

        return farthest_loop_distance, num_interior_points
```

I spent quite a bit of time here writing that `grids` helper module. But it was
worth it for two reasons:

1. It shortened my solution quite a bit, and it'll also shorten my solutions to
the other AoC grid puzzles. (And there are a lot of them!)
2. Now that I've written it, I'll _never_ have to write it again.
