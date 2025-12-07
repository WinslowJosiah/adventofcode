---
year: 2025
day: 5
title: "Cafeteria"
slug: 2025/day/5
pub_date: "2025-12-05"
# concepts: [higher-order-functions]
---
## Part 1

It's another good day to use a [`range`](https://docs.python.org/3/library/stdtypes.html#typesseq-range).
Here, we see ranges of ingredient IDs (similar to [Day 2](/solutions/2025/day/2)),
as well as individual ingredient IDs that may or may not be in those ranges.
First, let's parse all of this.

```py title="2025\day05\solution.py"
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_ranges, raw_ids = map(str.splitlines, self.input)

        ranges: list[range] = []
        for raw_range in raw_ranges:
            start, stop = map(int, raw_range.split("-"))
            # NOTE The stop of the range is inclusive.
            ranges.append(range(start, stop + 1))
        ids = [int(_id) for _id in raw_ids]
        ...
```

To count the ingredient IDs that are in any of the ranges, we can use a
generator that iterates through an ID only if `any` of the ranges contain it,
and `sum` up a `1` for each ID that fits. (This is one of the generator-counting
tricks I introduced on [Day 4](/solutions/2025/day/4).)

```py title="2025\day05\solution.py"
class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...
        return sum(1 for _id in ids if any(_id in r for r in ranges))
```

Pretty straightforward in my opinion... but maybe that's because the stuff we're
doing is familiar.

## Part 2

_Here's_ where it gets interesting.

In preparation for this year's Advent of Code, someone warned me that I might
want to implement what she called a [`rangeset`](https://github.com/LyricLy/aoc/blob/4b731404746fbfaf920987bc1a026f515513e3af/2024/common/rangeset.py)
-- a `set`-like data structure that stores numbers as _ranges_, instead of as
individual numbers. And once I saw the prompt for Part 2, I knew that something
like that would make this puzzle trivial.

Sadly, I haven't prepared anything like that yet. So in lieu of using a
`rangeset`, let's see what we can do with just our bare hands... and maybe
Python's [built-in functions](https://docs.python.org/3/library/functions.html)
as well.

First, let's factor out our input parsing.

```py title="2025\day05\solution.py" ins=/def (_parse_input)/ ins="tuple[list[range], list[int]]" ins={13,16}
class Solution(StrSplitSolution):
    ...

    def _parse_input(self) -> tuple[list[range], list[int]]:
        raw_ranges, raw_ids = map(str.splitlines, self.input)

        ranges: list[range] = []
        for raw_range in raw_ranges:
            start, stop = map(int, raw_range.split("-"))
            # NOTE The stop of the range is inclusive.
            ranges.append(range(start, stop + 1))
        ids = [int(_id) for _id in raw_ids]
        return ranges, ids

    def part_1(self) -> int:
        ranges, ids = self._parse_input()
        return sum(1 for _id in ids if any(_id in r for r in ranges))
```

The naive thing to do here would be to simply total the lengths of all of the
ranges. But as the sample input makes clear, the ranges _could_ indeed be
overlapping, which would lead to an overcount.

```py title="2025\day05\solution.py"
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ranges, _ = self._parse_input()
        # FIXME Doesn't work! The ranges could be overlapping.
        return sum(len(r) for r in ranges)
```

To prevent overcounting, we'll first need to make sure that the ranges are _not_
overlapping. We can do that by merging pairs of ranges if they overlap with each
other; the resulting range will start at the earlier start point, and stop at
the later stop point.

As a pre-processing step, we can sort the ranges by their starting points. Once
this is done, only pairs of adjacent ranges will even have a _chance_ of
overlapping with each other, and we can try merging these sorted ranges from
left to right. We can pass a key function to `sorted` for this; the
[`operator.attrgetter`](https://docs.python.org/3/library/operator.html#operator.attrgetter)
function can be used to sort by the `start` attribute.

```py title="2025\day05\solution.py"
from operator import attrgetter

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ranges, _ = self._parse_input()

        merged_ranges: list[range] = []
        # Loop through ranges in ascending order
        for right in sorted(ranges, key=attrgetter("start")):
            ...
        ...
```

:::note
`operator.attrgetter` is a function that takes in an attribute name as a string,
and returns _another_ function that will fetch that attribute from the object
passed to it.

```py
>>> from operator import attrgetter
>>> get_start = attrgetter("start")
>>> get_start(range(10, 14))
10
```

This may look strange if you've never seen it before, but it's an example of a
[higher-order function](https://en.wikipedia.org/wiki/Higher-order_function) --
a function that either takes a function as input or returns a function as
output.
:::

As we loop through each range, we'll consider it the `right` range, and the
latest range in `merged_ranges` (whatever it is) the `left` range. Then, one of
two things will happen:

- If we _don't_ need to merge `left` and `right` -- or if `merged_ranges` is empty
and `left` doesn't exist -- we will include `right` as-is.
- If we _do_ need to merge `left` and `right`, we will replace the latest entry
of `merged_ranges` with a merged version of `left` and `right` -- using the
earlier start point and the later stop point.

Because of the way we ordered the ranges, checking whether we need to merge
`left` and `right` is as simple as checking where `left.stop` is relative to
`right.start`:

- If `left.stop` is _before_ `right.start`, they don't overlap, and we don't
need to merge them.
- If `left.stop` is _equal to_ `right.start`, they sit directly next to each
other without leaving a gap, and it's okay to merge them.
- If `left.stop` is _after_ `right.start`, they overlap, and we need to merge
them.

Putting it all together takes some care, but it's not too bad. (One thing I
decided to do is use `:=` -- the ["walrus operator"](https://docs.python.org/3/reference/expressions.html)
-- to store `left` _within_ the merging condition, because I think it makes the
condition slightly less awkward.)

```py title="2025\day05\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        for right in sorted(ranges, key=attrgetter("start")):
            # If there is no left range to merge with, or the ranges
            # don't overlap, append the right range as-is
            if (
                not merged_ranges
                or (left := merged_ranges[-1]).stop < right.start
            ):
                merged_ranges.append(right)
            # Otherwise, merge and replace the left range
            else:
                merged_ranges[-1] = range(
                    min(left.start, right.start),
                    max(left.stop, right.stop),
                )
        ...
```

Once all the ranges are merged, none of them will be overlapping, and so we can
use our naive range-counting approach from before.

```py title="2025\day05\solution.py" ins="merged_ranges"
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        # NOTE By now, none of the ranges should be overlapping, so
        # their lengths can now be totaled directly.
        return sum(len(r) for r in merged_ranges)
```

It was a bit tricky to figure out the best way to do this, but we did get there!
Though perhaps I'll want to create a `rangeset` class for other puzzles like
this... maybe some other time.
