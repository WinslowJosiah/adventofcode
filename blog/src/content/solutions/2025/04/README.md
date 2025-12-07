---
year: 2025
day: 4
title: "Printing Department"
slug: 2025/day/4
pub_date: "2025-12-04"
# concepts: []
---
## Part 1

Another day, another grid puzzle. I was _wondering_ how early we'd see one this
year.

I'll be breaking out the [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
I introduced on [2023 Day 10](/solutions/2023/day/10) for this; it has a
`parse_grid` function which takes a list of rows and returns a mapping between
grid points and their tiles.

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

I gave this function an `ignore_chars` parameter, so that any tiles with certain
characters in them don't appear in the final grid. We're only focusing on the
tiles with paper rolls on them, so we can ignore the floor tiles (`.`). Also, we
only care about the _locations_ of the paper tiles (the characters are all the
same), so I take the `keys` of the resulting mapping and put them in a `set`.

```py title="2025\day04\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        rolls = set(parse_grid(self.input, ignore_chars=".").keys())
        ...
```

My `grids` module also has a `neighbors` function which iterates through the
neighbors of a grid point. Take a look at the code of the `grids` module if you
want to see how it works, but the basic thing to know is that
`neighbors(point, num_directions=8)` will yield all 8 neighbors of `point` --
up, down, left, right, and the four diagonal directions.

We can use this to write a function to check whether a point on the floor is
accessible. `neighbors` doesn't check for us whether the points it returns are
in the grid, so we have to do that [explicitly](https://pep20.org/#explicit). So
we can easily count a point's neighboring paper rolls that are in the set of all
`rolls`, and we'll want to return whether or not this count is less than 4.

```py title="2025\day04\solution.py"
def is_accessible(rolls: set[GridPoint], point: GridPoint) -> bool:
    num_neighbors = sum(
        1
        for n in neighbors(point, num_directions=8)
        if n in rolls
    )
    return num_neighbors < 4
```

With this function in hand, we can use it to count the number of accessible
paper rolls.

```py title="2025\day04\solution.py" ins={6}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        rolls = set(parse_grid(self.input, ignore_chars=".").keys())
        return sum(is_accessible(rolls, point) for point in rolls)
```

:::tip
One common Python idiom for counting the items in a generator `gen` is
`sum(1 for _ in gen)`. (The alternate approach `len(list(gen))` also works, but
that wastes memory by storing every single item in a `list`.)

If you want to count only the items that fit some condition `cond`, this can be
changed to `sum(1 for g in gen if cond(g))`. I used this in the body of
`is_accessible` to count the number of neighboring points `n` where `n in rolls`
is true.

And if you know that `cond(g)` will only be `True` or `False`, another way to
count the items that fit the condition would be `sum(cond(g) for g in gen)`;
this works because [`bool` is a subclass of `int`](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool),
and `True` and `False` are treated like `1` and `0` in calculations. I used this
in the body of my Part 1 solution to count the points `point` where
`is_accessible(rolls, point)` is true.[^could-have-used]
:::

[^could-have-used]: I could have used the `sum(cond(g) for g in gen)` idiom in
`is_accessible` as well -- after all, `n in rolls` will return only `True` or
`False` -- but in that case, I felt that that was less [readable](https://pep20.org/#readability).

## Part 2

Now that we know which paper rolls are accessible, we want to actually _remove_
them. And not just once; we want to remove the paper rolls until we can't
anymore. This isn't too bad; we just need to remove these paper rolls in a loop,
and keep track of a running total of removed paper rolls.

Firstly, we need to find the locations of every accessible paper roll, and
immediately `break` out of the loop if there are none.

```py title="2025\day04\solution.py"
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        rolls = set(parse_grid(self.input, ignore_chars=".").keys())

        total = 0
        while True:
            accessible_points = {
                point
                for point in rolls
                if is_accessible(rolls, point)
            }
            # Loop until no more rolls are accessible
            if not accessible_points:
                break
            ...
        ...
```

Then we need to tally up those accessible paper rolls, and remove them from the
set of all `rolls`. (This is why I made `accessible_points` a set; I can use
`-=` to remove those points from the `rolls` set!)

```py title="2025\day04\solution.py"
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...
        while True:
            ...
            total += len(accessible_points)
            rolls -= accessible_points

        return total
```

Finally, we return our running total.

This was surprisingly easy for an AoC grid puzzle... but I'll take it!
