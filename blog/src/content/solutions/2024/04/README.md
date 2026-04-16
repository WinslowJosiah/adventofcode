---
year: 2024
day: 4
title: "Ceres Search"
slug: 2024/day/4
pub_date: "2026-04-16"
# concepts: []
---
## Part 1

Another day, another grid puzzle. And another excuse to bring out my AoC
[`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py).

I won't reproduce my entire `grids` module here, so I'd encourage you to read
its source code if you're interested in how it works. But for our purposes,
here's all we need to know about it:

- I represent a `GridPoint` -- row/column locations in a grid -- as a `tuple` of
two `int`s. The functions `add_points` and `subtract_points` allow these
`GridPoint`s to be added and subtracted.
- I represent a `Grid` as a `dict` where the keys are `GridPoint`s and the
values are the grid's items. `parse_grid` is a function that creates a new
`Grid` from a list of string lines.
- The convenience function `offsets` yields offset directions as `GridPoint`s.
For example:
    - `offsets(num_directions=8)` yields offsets for up, down, left, right, and
    the four diagonals.
    - `offsets(num_directions=4, diagonals=True)` yields offsets for the four
    diagonals only.

As an illustration, here's what one of the example grids looks like after
passing it to `parse_grid`.

```py
{(0, 0): '.', (0, 1): '.', (0, 2): 'X', (0, 3): '.', (0, 4): '.', (0, 5): '.',
 (1, 0): '.', (1, 1): 'S', (1, 2): 'A', (1, 3): 'M', (1, 4): 'X', (1, 5): '.',
 (2, 0): '.', (2, 1): 'A', (2, 2): '.', (2, 3): '.', (2, 4): 'A', (2, 5): '.',
 (3, 0): 'X', (3, 1): 'M', (3, 2): 'A', (3, 3): 'S', (3, 4): '.', (3, 5): 'S',
 (4, 0): '.', (4, 1): 'X', (4, 2): '.', (4, 3): '.', (4, 4): '.', (4, 5): '.'}
```

With that, we can get to finding every **XMAS** word in the word search grid. In
fact, we can actually follow the same algorithm a human might use:

1. Scan through the grid for the starting letter of the word (**X**, in this
case).
2. For each possible starting location, look outwards from there in all 8
directions for the remaining letters in line (**MAS**, in this case).
3. If all letters of the word are found, add 1 to a grand total of found words.

```py title="2024\day04\solution.py" {"1":8-11} {"2":13-19} {"3":21}
from ...utils.grids import add_points, offsets, parse_grid

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        # Find all start characters of an XMAS
        for start, start_char in grid.items():
            if start_char != "X":
                continue

            # Scan for the rest of the characters in all directions
            for offset in offsets(num_directions=8):
                point = start
                for char in "MAS":
                    point = add_points(point, offset)
                    if grid.get(point) != char:
                        break
                else:
                    total += 1

        return total
```

Hopefully it's easy to see how the code implements each step. The only slightly
obscure thing to understand would be the `else` block after the
`for char in "MAS"` loop; believe it or not, an `else` block on a `for` loop is
[entirely legal](https://docs.python.org/3/tutorial/controlflow.html#else-clauses-on-loops),
and the `else` block runs if the loop wasn't broken out of with `break`.

## Part 2

We weren't supposed to find **XMAS**... we're supposed to find X-**MAS**! Sounds
different, but not _too_ different.

We'll need to use a slightly different algorithm to find all occurrences of an
X-**MAS**.

1. Scan through the grid for **A** letters which could be the crossing point of
an X-**MAS**.
2. For all four diagonal directions, check for an **M** going forwards and an
**S** going backwards. This forms a single **MAS**; we'll want to count how many
of them we see for this center point.
3. If two **MAS**es cross here, add 1 to a grand total.

```py title="2024\day04\solution.py" ins=", subtract_points" {"1":9-12} {"2":14-21} {"3":23-25}
from ...utils.grids import add_points, offsets, parse_grid, subtract_points

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        # Find all center characters of an X-shaped MAS
        for center, center_char in grid.items():
            if center_char != "A":
                continue

            num_mas = 0
            # Scan for M and S in diagonal directions
            for offset in offsets(num_directions=4, diagonals=True):
                forward = add_points(center, offset)
                backward = subtract_points(center, offset)
                # MAS has M and S in opposite directions from the A
                if grid.get(forward) == "M" and grid.get(backward) == "S":
                    num_mas += 1

            # An X-MAS consists of two MASes that cross
            if num_mas == 2:
                total += 1

        return total
```

These solutions turned out to be a straightforward translation from ideas to
code, thanks to my `grids` module abstracting away a lot of implementation
details. That's the value of having good helper libraries and functions: they
allow you to think less about the _representation_ of things and more about how
to _use_ them.
