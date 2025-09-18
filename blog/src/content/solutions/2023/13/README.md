---
year: 2023
day: 13
title: "Point of Incidence"
slug: 2023/day/13
pub_date: "2025-10-23"
# concepts: []
---
## Part 1

While each block of terrain _looks_ like a grid, we don't have to treat it like
one; in fact, leaving the blocks as lists of strings simplifies some of our
work.

First, let's create a function that will find the reflection point in a list of
rows. We'll use a neat trick to apply it to the columns later.

If we have an index (`i`) into a list of rows (`rows`), then `rows[:i]` gives us
the items above that index, and `rows[i:]` gives us the items below (and
including) that index. If there is a mirror at that index, each row below going
down should be the same as the corresponding row above going up.

Once we have the rows `above` and the rows `below`, we can loop through each
pair of corresponding rows using `zip(reversed(above), below)`. (Note that the
rows above are reversed, because the last row above will be the one closest to
the mirror, and we're moving outwards from there.) The location of the mirror
will be the one where `all` such pairs of rows are equal.

```py title="2023\day13\solution.py"
from collections.abc import Sequence

def find_mirror_row(rows: Sequence[Sequence[str]]) -> int:
    # NOTE 0 is not included, because the rows above would be empty, and
    # we'd detect this as a valid reflection. That's not what we want.
    for i in range(1, len(rows)):
        above, below = rows[:i], rows[i:]
        if all(a == b for a, b in zip(reversed(above), below)):
            return i
    return 0
```

`zip` will stop looping at the end of the shortest sequence it receives, so we
won't be comparing rows outside of the grid. And as a failsafe, we return 0 if
we don't find a mirror between any rows.

Next, let's create a function to score a single block of terrain. Row-mirrors
are worth 100 times their location, and column-mirrors are worth their location.
(I decided to return 0 if no mirror was found anywhere, but because AoC inputs
are well-formed, this should never happen.)

```py title="2023\day13\solution.py" "list(zip(*rows))"
def score_block(block: str) -> int:
    rows = block.splitlines()
    if row := find_mirror_row(rows):
        return 100 * row
    if col := find_mirror_row(list(zip(*rows))):
        return col
    return 0
```

And here's where the neat trick comes into play. If we have a list of rows
called `rows`, then `zip(*rows)` will iterate through the columns; this is
because it's looping through each item of every row in parallel. (This is a very
useful trick to **transpose** a series of rows.)

```py
>>> rows = ["line", "area", "vows", "ante"]
>>> list(zip(*rows))
[('l', 'a', 'v', 'a'),
 ('i', 'r', 'o', 'n'),
 ('n', 'e', 'w', 't'),
 ('e', 'a', 's', 'e')]
```

Finally, we can `sum` up the scores of each block to solve Part 1.

```py title="2023\day13\solution.py"
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        return sum(score_block(block) for block in self.input)
```

## Part 2

Turns out the mirrors have exactly one "smudge", and the reflections are
identical except for this smudge. So our `find_mirror_row` function should take
that into account.

First, though, we should create a function that will count the number of smudges
in two rows (i.e. number of differences). This looks like a job for `zip`[^lots-of-zips]
and `sum`.

[^lots-of-zips]: Wow, lots of `zip`s today, aren't there?

```py title="2023\day13\solution.py"
def num_smudges(a: Sequence[str], b: Sequence[str]) -> int:
    return sum(char_a != char_b for char_a, char_b in zip(a, b))
```

Now we can use this function to count the number of smudges in a reflection.

```py title="2023\day13\solution.py" ins=", smudges: int" ins=", smudges: int = 0" ins=", smudges" ins={7-8}
def find_mirror_row(rows: Sequence[Sequence[str]], smudges: int) -> int:
    # NOTE Row 0 is not included, because the rows above would be empty,
    # and we'd detect this as a valid reflection. We don't want that.
    for i in range(1, len(rows)):
        above, below = rows[:i], rows[i:]
        if (
            sum(num_smudges(a, b) for a, b in zip(reversed(above), below))
            == smudges
        ):
            return i
    return 0

def score_block(block: str, smudges: int = 0) -> int:
    rows = block.splitlines()
    if row := find_mirror_row(rows, smudges):
        return 100 * row
    if col := find_mirror_row(list(zip(*rows)), smudges):
        return col
    return 0
```

And lastly, we can pass in the number of smudges we need for Part 2 (one
smudge).

```py title="2023\day13\solution.py" ins={6-7}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return sum(score_block(block, smudges=1) for block in self.input)
```

This was the second row-list day we've had this year (the first one being
[Day 3](/solutions/2023/day/3)). I find these kinds of days rather nice,
especially when I get to use that `zip(*rows)` trick.
