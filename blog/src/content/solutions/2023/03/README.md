---
year: 2023
day: 3
title: "Gear Ratios"
slug: 2023/day/3
pub_date: "2025-10-09"
# concepts: [regex]
---
## Part 1

The first grid-based puzzle I've ever completed in Advent of Code! And honestly,
it's not too bad -- especially compared to the ones I'd see _later_. In fact, I
don't even need to treat the input like a _grid_; it's fine to treat it as a
list of string lines.

We need to find every number that's surrounded by a symbol (i.e. not a digit or
dot). To do that, we'll find every number _at all_, and check whether it's
surrounded by a symbol. We can make short work of finding the numbers using some
regexes.

```py title="2023\day03\solution.py" /if (\\(\\))/
import re

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        total = 0
        for row_index, row in enumerate(self.input):
            for number in re.finditer(r"\d+", row):
                start, end = number.span()
                part_num = int(number.group())

                if ():  # TODO Add is-surrounded-by-symbol check
                    total += part_num

        return total
```

:::note
While `re.findall` simply returns the matching strings, `re.finditer` yields
`Match` objects with extra information about the match (like where exactly it
is).

Because we'll be using the location of the match later in our code, I decided to
use `re.finditer` here.
:::

We can also check whether each number is surrounded by a symbol using -- what
else? -- more regexes.

The pattern `[^\d.]` will match any single character that is not a digit (`\d`)
or a dot (`.`). We'll [`re.compile`](https://docs.python.org/3/library/re.html#re.compile)
that pattern to make it more efficient to search for it repeatedly (and let us
specify a starting and ending position for our searches).

```py title="2023\day03\solution.py" ins={5}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        RE_SYMBOL = re.compile(r"[^\d.]")
        ...
```

The area around the number (in which we want to search for symbols) extends from
the previous to the next row, and from the column before first to the column
after last. The search will be in the form of a carefully constructed expression
inside of `any`; what we're checking is whether any of the previous, current, or
next rows return a match when we search them between the specified column
boundaries. (But beware of off-by-one errors!)

```py title="2023\day03\solution.py" ins={10-16}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        for row_index, row in enumerate(self.input):
            for number in re.finditer(r"\d+", row):
                ...

                # Check for symbols in previous, current, and next rows
                if any(
                    RE_SYMBOL.search(
                        self.input[symbol_row_index], start - 1, end + 1,
                    )
                    for symbol_row_index in range(row_index - 1, row_index + 2)
                ):
                    ...
        ...
```

With that, we're _almost_ done. While the `search` method handles out-of-bounds
columns gracefully, trying to get an out-of-bounds row raises an `IndexError`.

There are a few ways to handle this, but the one I went with is padding the grid
with a row of all dots on the top and bottom. That way, no symbols or numbers
will be found there, and these rows can be accessed without errors or bounds
checking.[^empty-rows]

[^empty-rows]: Because out-of-bounds columns are handled by the `search` method,
the padding rows _technically_ could be empty. And thanks to the fact that an
index of `-1` signifies the end of the list, the padding _technically_ only
needs to be at the end. But at that level of optimization, the code would become
a bit [hard to explain](https://pep20.org/#hard).

```py title="2023\day03\solution.py" ins={4-6,9} ins=/grid(?!_width| with| =)/
...

class Solution(StrSplitSolution):
    def _pad_input(self) -> list[str]:
        grid_width = len(self.input[0])
        return ["." * grid_width, *self.input, "." * grid_width]

    def part_1(self) -> int:
        grid = self._pad_input()
        RE_SYMBOL = re.compile(r"[^\d.]")

        total = 0
        for row_index, row in enumerate(grid):
            for number in re.finditer(r"\d+", row):
                ...

                # Check for symbols in previous, current, and next rows
                if any(
                    RE_SYMBOL.search(
                        grid[symbol_row_index], start - 1, end + 1,
                    )
                    for symbol_row_index in range(row_index - 1, row_index + 2)
                ):
                    ...
        ...
```

## Part 2

There's not much different to do for Part 2. Instead of finding _any_ symbols,
we're finding only the _asterisks_; we also need to keep track of the position
of each gear, and the part numbers that see them.

`defaultdict(list)` is a good choice for a mapping between a gear's position and
the list of part numbers that see it. Each part number can be appended in a
nested loop like so (modifying the regex from Part 1 to find all occurrences of
gears):

```py title="2023\day03\solution.py" ins={1,9,11,17-23}
from collections import defaultdict
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        grid = self._pad_input()
        RE_GEAR = re.compile(r"\*")

        gears: dict[tuple[int, int], list[int]] = defaultdict(list)
        for row_index, row in enumerate(grid):
            for number in re.finditer(r"\d+", row):
                start, end = number.span()
                part_num = int(number.group())

                # Find gears in previous, current, and next rows
                for gear_row_index in range(row_index - 1, row_index + 2):
                    for gear_match in RE_GEAR.finditer(
                        grid[gear_row_index], start - 1, end + 1,
                    ):
                        gear_pos = gear_row_index, gear_match.start()
                        gears[gear_pos].append(part_num)
        ...
```

The last thing to change from Part 1 is the value to return. [`operator.mul`](https://docs.python.org/3/library/operator.html#operator.mul)
can multiply two numbers for us -- once we verify that there _are_ two numbers,
of course -- and we can `sum` up all the results for our final answer.

```py title="2023\day03\solution.py" ins={1,9}
from operator import mul
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        return sum(mul(*nums) for nums in gears.values() if len(nums) == 2)
```

I like the kinds of grid-based puzzles that you don't have to _think_ of as
grid-based.
