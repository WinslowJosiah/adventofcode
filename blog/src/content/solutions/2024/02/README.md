---
year: 2024
day: 2
title: "Title"
slug: 2024/day/2
pub_date: "2026-04-11"
# concepts: []
---
## Part 1

Today's input is in the form of many lists of numbers, one per line. Parsing
each line can be done with a simple list comprehension.

```py title="2024\day02\solution.py"
def parse_report(line: str) -> list[int]:
    return [int(level) for level in line.split()]
```

Each list of numbers is a report on "levels" of... something, and we have to
check which ones are "safe". A "safe" report fits two requirements:

> - The levels are either _all increasing_ or _all decreasing_.
> - Any two adjacent levels differ by _at least one_ and _at most three_.

It'll be simpler to first consider how to check this for an increasing list of
levels. If we iterate through each pair `a` and `b` of adjacent levels using
[`itertools.pairwise`](https://docs.python.org/3/library/itertools.html#itertools.pairwise),
we'll want to check whether `b - a` is between 1 and 3 for every single pair.

```py title="2024\day02\solution.py" ins={1-2}
from collections.abc import Sequence
from itertools import pairwise

def is_safe_increasing(report: Sequence[int]) -> bool:
    return all(1 <= b - a <= 3 for a, b in pairwise(report))
```

:::tip
If you want to make multiple comparisons at once, you can chain them together;
for example, `a <= b <= c` is the same as `a <= b and b <= c`. This is
especially useful if `b` is a complicated expression.
:::

This lets us check whether a report is safe, but only if it happens to be
_increasing_. But if the report is _decreasing_, it looks just like an
increasing report, so we can reverse it and check if _that_ is a safe increasing
report.

```py title="2024\day02\solution.py"
def is_safe(report: Sequence[int]) -> bool:
    return is_safe_increasing(report) or is_safe_increasing(report[::-1])
```

We can then use this safety-checking function to count how many reports are
safe, using a simple `sum` expression.

```py title="2024\day02\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(is_safe(parse_report(line)) for line in self.input)
```

:::tip
There are a few ways to count the items in a list that fit a condition, but if
you know that every value will only be `True` or `False`, there's one
[obvious way](https://pep20.org/#obvious) to do it:
`sum(cond(item) for item in lst)`.

This works because [`bool` is a subclass of `int`](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool),
and calculations involving `True` and `False` will treat them as `1` and `0`
respectively.
:::

## Part 2

Apparently each report is allowed to have up to one bad level and still be
considered safe. In other words, we'll want to do our safety check for versions
of each report with one level removed.

For this, we can use a neat little-known feature of [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations):
each combination it returns will have its items in the _same order_ as they were
given! So if the length of each combination is the length of the report minus 1,
each combination will look like a version of the full report with one level
removed -- exactly what we want!

```py
>>> from itertools import combinations
>>> report = [1, 2, 3, 4]
>>> list(combinations(report, len(report) - 1))
[(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)]
```

We can now directly check whether `any` of these combinations are safe, and
count them like we did before.

```py title="2024\day02\solution.py" ins="combinations, "
from itertools import combinations, pairwise

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        reports = [parse_report(line) for line in self.input]
        return sum(
            # NOTE We don't need to check whether the original report is
            # safe; using the "Problem Dampener" on a safe report
            # doesn't change its safeness.
            any(
                is_safe(levels)
                # NOTE Each returned combination will be in the same
                # order, but with one item removed.
                for levels in combinations(report, len(report) - 1)
            )
            for report in reports
        )
```

It's nice when I can use such a neat feature of the standard library...
especially when my [initial solution](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2024/day02/__init__.py)
did the same thing in a more awkward way.
