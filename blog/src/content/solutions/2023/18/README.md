---
year: 2023
day: 18
title: "Lavaduct Lagoon"
slug: 2023/day/18
pub_date: "2025-11-03"
# concepts: [higher-order-functions]
---
## Part 1

We are calculating the area of a large polygon. This reminds me of [Day 10](/solutions/2023/day/10)
-- and in fact, this is secretly the reason I put that `interior_area` formula
from that day in my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py).
In fact, plenty of things from that module will be useful for us today.

We can proceed much like we did on Day 10, appending points to a `points` list
as we travel through the trench.

```py title="2023\day18\solution.py"
DIRECTIONS = {
    "U": Direction.UP.offset,
    "R": Direction.RIGHT.offset,
    "D": Direction.DOWN.offset,
    "L": Direction.LEFT.offset,
}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        points: list[GridPoint] = [(0, 0)]
        for line in self.input:
            direction, distance_str, _ = line.split()
            for _ in range(int(distance_str)):
                points.append(add_points(DIRECTIONS[direction], points[-1]))
        ...
```

Just like on Day 10, the [shoelace formula](https://en.wikipedia.org/wiki/Shoelace_formula)
can be used to calculate the area of the polygon, and [Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem)
can be used to relate the area to the number of interior points. This time, what
we want is the number of interior _and_ boundary points, so we also add the
number of points in our `points` list to get our answer.

```py title="2023\day18\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        area = interior_area(points)
        # NOTE Pick's theorem relates the area, number of interior grid
        # points, and number of boundary grid points of a simple lattice
        # polygon. This formula follows from simple algebra.
        num_interior_points = int(area - len(points) / 2 + 1)
        return num_interior_points + len(points)
```

It's interesting that we don't seem to be using the colors, though. Why are they
in our puzzle input?

## Part 2

Oh. _That's_ why.

Well, we have to extract the directions and distances from the hex digits of the
color now. That's easy; we can use the optional `base` argument of [`int`](https://docs.python.org/3/library/functions.html#int)
to interpret the strings as base-16 numbers. But those distances are going to be
_big_, so we won't be able to store every single point along the trench; we
should instead only store the corners.

We'll end up doing the same things for Parts 1 and 2, but with different ways to
convert lines to direction offsets and distances. One neat way to do this is
with a [higher-order function](https://en.wikipedia.org/wiki/Higher-order_function)
-- a kind of function that can receive or return _other functions_! Let me show
you what I mean.

```py title="2023\day18\solution.py" ins={1,8,12} ins="_solve" "get_instruction"
from collections.abc import Callable

...

class Solution(StrSplitSolution):
    def _solve(
            self,
            get_instruction: Callable[[str], tuple[GridPoint, int]],
    ) -> int:
        points: list[GridPoint] = [(0, 0)]
        for line in self.input:
            offset, distance = get_instruction(line)
            ...
```

Here, our `_solve` function will take in a function -- `get_instruction` -- as
input, and it will use that function to parse the direction offset and distance
from the next line of input. The `_solve` function doesn't need to know exactly
how that's done; it just needs to _do_ it.

And in our Part 1 and Part 2 solutions, we can define these line-parsing
functions, and we can pass them into our `_solve` function. (Note the use of
`int` with a `base=16` argument, to parse the distance in Part 2 as base-16!)

```py title="2023\day18\solution.py" ins={7,13-16,19-24} "parse_line"
DIRECTIONS = {
    "U": Direction.UP.offset,
    "R": Direction.RIGHT.offset,
    "D": Direction.DOWN.offset,
    "L": Direction.LEFT.offset,
}
OFFSETS = list(DIRECTIONS.values())

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        def parse_line(line: str) -> tuple[GridPoint, int]:
            direction, distance_str, _ = line.split()
            return DIRECTIONS[direction], int(distance_str)
        return self._solve(parse_line)

    def part_2(self) -> int:
        def parse_line(line: str) -> tuple[GridPoint, int]:
            _, _, hex_str = line.split()
            offset = OFFSETS[int(hex_str[-2])]
            distance = int(hex_str[2:-2], base=16)
            return offset, distance
        return self._solve(parse_line)
```

:::note
We've actually used some _other_ higher-order functions so far this year;
`collections.defaultdict` and `functools.cache` are two examples from the
standard library, and the `find_shortest_paths` function I showcased on [Day 17](/solutions/2023/day/17)
is one example that's custom-made. A higher-order function is a very useful tool
to have in your back pocket, so I'd recommend getting comfortable with
using/writing them!
:::

Now for the rest of the `_solve` function. We're no longer keeping track of
every single point along the boundary, so we'll tally them separately. And
instead of adding the offset to our position many times, we'll scale the offset
by the distance and add _that_ to our position.

```py title="2023\day18\solution.py" ins={11,13-14,16} ins=/\\((scaled_offset)/ ins=/[+\\-] (num_boundary_points)/
from collections.abc import Callable

...

class Solution(StrSplitSolution):
    def _solve(
            self,
            get_instruction: Callable[[str], tuple[GridPoint, int]],
    ) -> int:
        points: list[GridPoint] = [(0, 0)]
        num_boundary_points = 0
        for line in self.input:
            offset, distance = get_instruction(line)
            scaled_offset = offset[0] * distance, offset[1] * distance
            points.append(add_points(scaled_offset, points[-1]))
            num_boundary_points += distance

        area = interior_area(points)
        # NOTE Pick's theorem relates the area, number of interior grid
        # points, and number of boundary grid points of a simple lattice
        # polygon. This formula follows from simple algebra.
        num_interior_points = int(area - num_boundary_points / 2 + 1)
        return num_interior_points + num_boundary_points
```

Otherwise, the process is basically the same, and we get our answer in no
time/memory flat.
