---
year: 2023
day: 11
title: "Cosmic Expansion"
slug: 2023/day/11
pub_date: "2025-10-22"
# concepts: []
---
## Part 1

Another day, another grid puzzle. But all we need are the locations of the `#`
characters; everything else can be figured out with some math.

```py title="2023\day11\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        points = list(parse_grid(self.input, ignore_chars=".").keys())
        ...
```

The `keys` of the result of `parse_grid` (the same `parse_grid` function as
[Day 10](/solutions/2023/day/10)) are the locations of the galaxies.[^keys-list]
Now we need to figure out where they'll be once the space between them is
expanded.

[^keys-list]: Technically, I could've just converted the grid itself to a list
to get the keys. But getting the keys [explicitly](https://pep20.org/#explicit)
makes it clearer what's going on.

Expanding will change the coordinates of all the existing rows and columns, so
let's write a function that will calculate these changes. We can use a neat set
comprehension to get a set of all non-empty row/column indices. Once we have
those, we can compile a list of expanded coordinates (where the expansion offset
increases if the coordinate index corresponds to an empty row/column).

```py title="2023\day11\solution.py"
def get_expanded_values(points: list[GridPoint], dim: int) -> list[int]:
    filled_lines = {p[dim] for p in points}
    max_coordinate = max(filled_lines)

    expanded_values: list[int] = []
    offset = 0
    for i in range(max_coordinate + 1):
        expanded_values.append(i + offset)
        if i not in filled_lines:
            offset += 1

    return expanded_values
```

This can be used to pretty easily get the coordinates of all of our expanded
galaxies.

```py title="2023\day11\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        expanded_rows = get_expanded_values(points, 0)
        expanded_columns = get_expanded_values(points, 1)
        expanded_points = [
            (expanded_rows[row], expanded_columns[col])
            for row, col in points
        ]
        ...
```

We'll need to sum up the distances between each pair of expanded points. The
type of thing we're looking for is "taxicab distance"; I have a function for it
in the [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
I talked about yesterday:

```py title="utils\grids.py"
def taxicab_distance(a: GridPoint, b: GridPoint) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

Summing this function over all pairs of expanded points (which we iterate
through with [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations))
gives us our answer!

```py title="2023\day11\solution.py"
from itertools import combinations

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        return sum(
            taxicab_distance(a, b)
            for a, b in combinations(expanded_points, 2)
        )
```

## Part 2

More of the same, except the space between galaxies gets _way bigger_. I'm
relieved that we went with a [sparse](https://pep20.org/#sparse) representation
of galaxy locations, because adding empty rows/columns to an actual 2D grid
would quickly blow up storage space!

In our `get_expanded_values` function, we only need to change one thing: instead
of the expansion offset increasing by 1 for an empty row/column, it increases by
`multiplier - 1` (so the resulting space between coordinates becomes the
`multiplier`).

```py title="2023\day11\solution.py" ins={4,} ins="multiplier - 1"
def get_expanded_values(
        points: list[GridPoint],
        dim: int,
        multiplier: int,
) -> list[int]:
    filled_lines = {p[dim] for p in points}
    max_coordinate = max(filled_lines)

    expanded_values: list[int] = []
    offset = 0
    for i in range(max_coordinate + 1):
        expanded_values.append(i + offset)
        if i not in filled_lines:
            offset += multiplier - 1

    return expanded_values
```

With that, we can simply pass in a multiplier of 2 for Part 1, and 1,000,000 for
Part 2.

```py title="2023\day11\solution.py" ins=/def (_solve)/ ins=", multiplier: int" ins=", multiplier" ins={19-20,22-23}
...

class Solution(StrSplitSolution):
    def _solve(self, multiplier: int) -> int:
        points = list(parse_grid(self.input, ignore_chars=".").keys())

        expanded_rows = get_expanded_values(points, 0, multiplier)
        expanded_columns = get_expanded_values(points, 1, multiplier)
        expanded_points = [
            (expanded_rows[row], expanded_columns[col])
            for row, col in points
        ]

        return sum(
            taxicab_distance(a, b)
            for a, b in combinations(expanded_points, 2)
        )

    def part_1(self) -> int:
        return self._solve(multiplier=2)

    def part_2(self) -> int:
        return self._solve(multiplier=1_000_000)
```
