---
year: 2024
day: 8
title: "Resonant Collinearity"
slug: 2024/day/8
pub_date: "2026-05-10"
# concepts: []
---
## Part 1

Another day, another grid puzzle. I'll again be breaking out the same custom
[`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
I used on [previous](/solutions/2024/day/4) [days](/solutions/2024/day/6); it
represents grids as `dict`s mapping grid locations to tiles.

For this puzzle, however, we need to be able to associate antenna "frequencies"
(i.e. all the non-dot characters in the grid) with every location of an antenna
with that "frequency". We can write a function to do this, creating a new `dict`
mapping antenna "frequencies" to lists of antenna locations, and appending to
the correct list when finding each antenna.

```py title="2024\day08\solution.py"
from collections import defaultdict

def find_antennas(grid: Grid[str]) -> dict[str, list[GridPoint]]:
    antennas: dict[str, list[GridPoint]] = defaultdict(list)
    for point, char in grid.items():
        if char != ".":
            antennas[char].append(point)
    return antennas
```

:::note
Instead of using a regular `dict` to store the antennas, I'm using a
[`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict).
If you try to get the value of a nonexistent key, a regular `dict` will raise a
`KeyError`; a `defaultdict`, on the other hand, will populate that key with a
default value.

The default value used for nonexistent keys will depend on a "factory function"
that you provide; for example, `defaultdict(list)` will call the `list` function
to create its default values, which means its default value will be an empty
list.
:::

The first thing our solution will do is call this antenna-finding function on
the input grid.

```py title="2024\day08\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        antennas = find_antennas(grid)
        ...
```

Each pair of like antennas will create two "antinodes", one in one direction and
one in the other. So I'll be using `itertools.permutations` to loop through
pairs of antennas, and calculating where their "antinode" would be in only one
direction: towards the second antenna.

:::tip
[`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
and [`itertools.permutations`](https://docs.python.org/3/library/itertools.html#itertools.permutations)
are two standard-library functions that give you a selection of items from a
larger collection. The main difference between them is in how that selection of
items is ordered:

- `permutations` gives you every possible ordering of each subset of items; for
example, if `("A", "B")` is returned, then so will `("B", "A")`.
- `combinations` gives you only _one_ ordering of each subset of items (the same
ordering they had in the original collection); for example, if `("A", "B")` is
returned, then `("B", "A")` is _not_ returned.

```py
>>> from itertools import combinations, permutations
>>> list(permutations("ABC", 2))
[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]
>>> list(combinations("ABC", 2))
[('A', 'B'), ('A', 'C'), ('B', 'C')]
```

:::

First, I use `subtract_points` to calculate the row/column distance between the
pair of antennas. Then I add that distance to the second antenna of the pair to
find the corresponding antinode, and if it's within the bounds of the grid, I
add it to a `set` of antinode locations (because we want to count unique
locations).

```py title="2024\day08\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        antinodes: set[GridPoint] = set()
        for locations in antennas.values():
            for a, b in permutations(locations, 2):
                distance = subtract_points(b, a)

                # The antinode is just past B
                antinode = add_points(b, distance)
                if antinode in grid:
                    antinodes.add(antinode)

        return len(antinodes)
```

The answer is then the length of our `set` of antinode locations. (In my case,
it's a few hundred. Those dastardly bunnies and their chocolate-marketing
tactics...)

## Part 2

Looks like there are more antinodes than we thought there were. The antennas'
signals propagate much further due to "resonant harmonics", so _every_ grid
location along the same line as two antennas[^exact-multiples] has an antinode.
We'll call these more abundant antinodes "strong", and the less abundant
antinodes from Part 1 "weak".

[^exact-multiples]: One question I had was, where would the antinodes be along
a line such as `..J.J..`? Would they be on `#.J.J.#` (exact integer multiples of
the antenna distance), or `##J#J##` (_all_ tiles that exactly hit the line)?
Apparently the answer is moot, because this kind of scenario happens to never
occur in the puzzle input.

The way we'll find these antinodes will be similar to before; the difference is,
we'll start at the second antenna of the pair (because it has an antinode), and
we'll move in that direction until we move off of the grid.

```py title="2024\day08\solution.py" ins="solve" ins="tuple[int, int]" ins=/weak_?/ ins=", len(strong_antinodes)" ins={9,19-23}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        antennas = find_antennas(grid)

        weak_antinodes: set[GridPoint] = set()
        strong_antinodes: set[GridPoint] = set()
        for locations in antennas.values():
            for a, b in permutations(locations, 2):
                distance = subtract_points(b, a)

                # The weak antinode is just past B
                antinode = add_points(b, distance)
                if antinode in grid:
                    weak_antinodes.add(antinode)

                # The strong antinodes are B and the locations past it
                antinode = b
                while antinode in grid:
                    strong_antinodes.add(antinode)
                    antinode = add_points(antinode, distance)

        return len(weak_antinodes), len(strong_antinodes)
```

Now the answer has grown to, in my case, over a _thousand_ antinodes. How
mediocre must the Easter Bunny's chocolate be to _require_ this?
