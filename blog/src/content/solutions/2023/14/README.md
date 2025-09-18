---
year: 2023
day: 14
title: "Parabolic Reflector Dish"
slug: 2023/day/14
pub_date: "2025-10-25"
# concepts: []
---
## Part 1

Today's puzzles are kinda interesting. I _could_ think of them as grid puzzles,
and break out the same `parse_grid` function I used on previous days.[^david-brownman]
But what if I _don't_?

[^david-brownman]: Check out [David Brownman's solution](https://advent-of-code.xavd.id/writeups/2023/day/14)
for an example of this kind of approach.

I didn't treat this as a "grid puzzle" [at first](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2023/day14/__init__.py);
I instead used some tricks with strings to roll the rocks around. Let's treat
the grid as a sequence of string rows, and see what those tricks were.

Part 1 asks us to roll some rocks upwards. The way we'll do this utilizes the
`zip(*rows)` trick from [Day 13](/solutions/2023/day/13); we'll transpose the
grid (so columns become rows), roll the rocks to the left, then transpose the
grid again (so rows go back to being columns). But how do we roll the rocks to
the left?

Let's start with some simple cases where there are no walls.

- `......` should become `......`.
- `...O..` should become `O.....`.
- `.O..O.` should become `OO....`.
- `OO.O.O` should become `OOOO..`.
- `OOOOOO` should become `OOOOOO`.

There are a few different ways to think about this, but here's what I landed on:

- We can use [`str.replace`](https://docs.python.org/3/library/stdtypes.html#str.replace)
on each of these strings to replace each `.` with empty space, so we get a
string containing only the rocks.
- We can use [`str.ljust`](https://docs.python.org/3/library/stdtypes.html#str.ljust)
on those rocks to pad the string of rocks to the original length, effectively
moving the empty space to the right of the rocks.

All we need is to do this to every section of the row surrounded by walls.
`row.split("#")` will work for splitting the row into these walled sections, and
`"#".join(...)` will join these sections back again. Let's put this together
into a function.

```py title="2023\day14\solution.py"
from collections.abc import Sequence

type Rows = tuple[Sequence[str], ...]
type Grid = tuple[str, ...]

def roll_left(grid: Rows) -> Grid:
    return tuple(
        "#".join(
            # For each section, we get only the rocks, and justify them
            # to the left of a string of dots
            section.replace(".", "").ljust(len(section), ".")
            for section in "".join(row).split("#")
        )
        for row in grid
    )
```

This allows us to write a function for rolling the rocks _up_, by transposing
the grid, rolling to the left, and transposing again.[^pyright-ignore]

[^pyright-ignore]: When I use the `zip(*rows)` trick, the inferred return type
is `zip[tuple[Any, ...]]`. This causes my type checker to fail if I try to pass
that to `roll_left`, because it expects the rows to be of type `Sequence[str]`,
but it thinks the rows are of type `Any`.

    This is very much not ideal, and using `typing.cast` to fix this makes the
    resulting code way more [dense](https://pep20.org/#sparse) and degrades its
    [readability](https://pep20.org/#readability). So I just put in a
    `# pyright: ignore` comment here (and elsewhere) to shut up the type checker
    this time, because [practicality beats purity](https://pep20.org/#practicality).

```py title="2023\day14\solution.py"
def roll_up(grid: Rows) -> Grid:
    return tuple(
        "".join(row)
        for row in zip(*roll_left(zip(*grid)))  # pyright: ignore[reportArgumentType]
    )
```

We can also write a function for getting the total load caused by the rocks.

```py title="2023\day14\solution.py"
def get_total_load(grid: Rows) -> int:
    return sum((len(grid) - i) * row.count("O") for i, row in enumerate(grid))
```

And now our job is easy!

```py title="2023\day14\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = tuple(self.input)
        return get_total_load(roll_up(grid))
```

## Part 2

First, let's finish the rest of our rolling functions. Rolling to the right will
be similar to rolling to the left, only we'll use [`str.rjust`](https://docs.python.org/3/library/stdtypes.html#str.rjust)
instead of `str.ljust`.

```py title="2023\day14\solution.py" "left" "ljust" "right" "rjust" ins={12-21}
def roll_left(grid: Rows) -> Grid:
    return tuple(
        "#".join(
            # For each section, we get only the rocks, and justify them
            # to the left of a string of dots
            section.replace(".", "").ljust(len(section), ".")
            for section in "".join(row).split("#")
        )
        for row in grid
    )

def roll_right(grid: Rows) -> Grid:
    return tuple(
        "#".join(
            # For each section, we get only the rocks, and justify them
            # to the right of a string of dots
            section.replace(".", "").rjust(len(section), ".")
            for section in "".join(row).split("#")
        )
        for row in grid
    )
```

In fact, there are so few differences between `roll_left` and `roll_right`...
why don't we just make a single function that can do both, and pass in
`str.ljust` or `str.rjust` as an argument?

```py title="2023\day14\solution.py" ins={3,15-16,18-19} ins=" or right" ins="justify_func(" ins=/(, )len\\(section\\)/ ins=/"\\."(\\))/
def _roll_horizontally(
        grid: Rows,
        justify_func: Callable[[str, int, str], str],
) -> Grid:
    return tuple(
        "#".join(
            # For each section, we get only the rocks, and justify them
            # to the left or right of a string of dots
            justify_func(section.replace(".", ""), len(section), ".")
            for section in "".join(row).split("#")
        )
        for row in grid
    )

def roll_left(grid: Rows) -> Grid:
    return _roll_horizontally(grid, str.ljust)

def roll_right(grid: Rows) -> Grid:
    return _roll_horizontally(grid, str.rjust)
```

:::tip
This works because doing `ljust` or `rjust` on a string directly is the same as
passing that string as the first argument of `str.ljust` or `str.rjust`.

```py
>>> "Hello".ljust(9)
"Hello...."
>>> "Hello".ljust(9) == str.ljust("Hello", 9)
True
>>> "World".rjust(9)
"....World"
>>> "World".rjust(9) == str.rjust("World", 9)
True
```

Calling a method this way can be done in general for _any_ instance method
defined on _any_ class.
:::

And rolling down will be similar to rolling up; the only difference will be
whether we `roll_left` or `roll_right` between transposing.

```py title="2023\day14\solution.py" ins={7-11}
def roll_up(grid: Rows) -> Grid:
    return tuple(
        "".join(row)
        for row in zip(*roll_left(zip(*grid)))  # pyright: ignore[reportArgumentType]
    )

def roll_down(grid: Rows) -> Grid:
    return tuple(
        "".join(row)
        for row in zip(*roll_right(zip(*grid)))  # pyright: ignore[reportArgumentType]
    )
```

Now that we can roll the rocks in any direction, we can do the spin cycles!

```py title="2023\day14\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        grid = tuple(self.input)
        NUM_CYCLES = 1_000_000_000

        for _ in range(NUM_CYCLES):
            grid = roll_up(grid)
            grid = roll_left(grid)
            grid = roll_down(grid)
            grid = roll_right(grid)

        return get_total_load(grid)
```

The only problem is, this won't finish in a timely manner. A billion spin cycles
is a _lot_, so this is probably going to end up in a loop. Let's find it.

```py title="2023\day14\solution.py" ins={6,8-15} ins=/for (i)/
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...
        states: dict[tuple[str, ...], int] = {}
        for i in range(NUM_CYCLES):
            if grid in states:
                print(
                    f"Loop found from i={states[grid]} to i={i} "
                    f"(length {i - states[grid]})"
                )
                break
            # Save this state
            states[grid] = i

            grid = roll_up(grid)
            ...
        ...
```

Here, I'm keeping track of the previous grid states and the `i` value they
appeared at in a `dict`.[^tuple-of-str] If the current grid is found in the
`dict`, that means we've seen it before, and there is a loop. When I run this on
the sample input, I get this output:

[^tuple-of-str]: This is secretly why I've been representing the grid
as a tuple of `str`s this whole time, because tuples of `str`s are hashable, and
thus can be a `dict` key.

```text
Loop found from i=2 to i=9 (length 7)
```

We end up in a loop! This means that the ending state must be somewhere within
this loop, and we've seen it already. But when?

The iterations we go through can be broken down into two portions: the portion
before the loop started, and the portion after the loop started. After the loop
starts, iterating one loop-length will always lead back to the same state, so we
can use the modulo operator (`%`) on the "after" portion to reflect this. So the
formula will be `loop_start + remaining % loop_length` -- once those values are
calculated, that is.

```py title="2023\day14\solution.py" ins={8-13}
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...
        states: dict[tuple[str, ...], int] = {}
        for i in range(NUM_CYCLES):
            # If a loop was detected, skip to ending state and break
            if (loop_start := states.get(grid)) is not None:
                remaining = NUM_CYCLES - loop_start
                loop_length = i - loop_start
                end_i = loop_start + remaining % loop_length
                grid = next(k for k, v in states.items() if v == end_i)
                break
            # Save this state
            states[grid] = i

            grid = roll_up(grid)
            ...
        ...
```

Once we find the state with that value as its `i` value (which we can do using
`next` with a generator expression), we can immediately `break` out. Now instead
of taking ~3 weeks (by my calculations), I get an answer in ~0.5 seconds on my
machine. Definitely an improvement!
