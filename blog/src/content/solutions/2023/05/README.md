---
year: 2023
day: 5
title: "If You Give A Seed A Fertilizer"
slug: 2023/day/5
pub_date: "2025-10-14"
# concepts: []
---
## Part 1

Today seems like a good day to use a [`range`](https://docs.python.org/3/library/stdtypes.html#typesseq-range).
It'll be simpler to use `range` objects here than to simply store the given
numbers as-is.

But first, let's do some input parsing. The first "block" of text defines a list
of seed numbers; the rest define a series of transformations to apply to those
seed numbers.

```py title="2023\day05\solution.py"
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_seeds, *blocks = self.input
        seeds = map(int, raw_seeds.removeprefix("seeds:").split())
        ...
```

The transformations are given in the form `(dest_start, source_start, size)`.
However, it'll be easier to apply the transformations if they're in the form
`(source_range, offset)` -- e.g. `(50, 98, 2)` should become
`(range(98, 98+2), 50-98)` -- so that any number in that range can simply be
added to the offset. Let's write some simple parsing functions for this.

```py title="2023\day05\solution.py"
# mask, offset
type Transformation = tuple[range, int]

def parse_range(line: str) -> Transformation:
    dest_start, source_start, size = map(int, line.split())
    return range(source_start, source_start + size), dest_start - source_start

def parse_transformations(block: str) -> list[Transformation]:
    # NOTE The first line of a block is its category; the rest are
    # ranges.
    return [parse_range(l) for l in block.splitlines()[1:]]
```

The transformations from each "block" of text ("seed-to-soil",
"soil-to-fertilizer", etc.) define a destination number for each source number.
If a source number is in any of the ranges, the offset from that range should be
applied; otherwise, the number is unchanged. We can write a simple function for
this, given a number and a list of transformations.

```py title="2023\day05\solution.py"
def transform_number(num: int, transformations: list[Transformation]) -> int:
    for mask, offset in transformations:
        if num in mask:
            return num + offset
    return num
```

After that, all we have left to do is gather the transformations, apply them to
each seed number, and take the `min` of the resulting location numbers.

```py title="2023\day05\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...
        transformation_groups = [parse_transformations(b) for b in blocks]
        locations: list[int] = []
        for seed in seeds:
            for transformations in transformation_groups:
                seed = transform_number(seed, transformations)
            locations.append(seed)

        return min(locations)
```

## Part 2

It's one of those days where Part 2 is difficult to brute-force. When I tried to
anyway, my computer froze for a while. So let's try something else.

Instead of using individual seed numbers, we're asked to use entire _ranges_ of
seed numbers. This looks like another job for `range`! Each range is defined by
groups of two numbers, which we can use [`itertools.batched`](https://docs.python.org/3/library/itertools.html#itertools.batched)
for (introduced in Python 3.12).

:::attention
Using `itertools.batched` will give us _non-overlapping_ groups of a given size.
Using `itertools.pairwise`, on the other hand, will give us _overlapping_ groups
of size 2.

```py
>>> from itertools import batched, pairwise
>>> seeds = [79, 14, 55, 13]
>>> list(batched(seeds, 2))
[(79, 14), (55, 13)]
>>> list(pairwise(seeds))
[(79, 14), (14, 55), (55, 13)]
```

These methods end up giving subtly different results, which can lead to bugs if
you're not careful.
:::

```py title="2023\day05\solution.py" ins={1,10-13}
from itertools import batched
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        raw_seeds, *blocks = self.input
        seeds = map(int, raw_seeds.removeprefix("seeds:").split())
        seed_ranges = [
            range(start, start + size)
            for start, size in batched(seeds, 2)
        ]
        ...
```

But what would it look like to apply a transformation to a _range_, instead of
to a number? Let's think about the different results, when the transformation
range overlaps different parts of the base range (mapped segments of the base
range are marked with `#`).

```text
        |  none   |  left   | middle |  right  |    all
------- | ------- | ------- | ------ | ------- | ---------
   base |   34567 |   34567 | 34567  | 34567   |   34567
   mask | 12      | 12345   |  456   |   56789 | 123456789
 result |   34567 |   ###67 | 3###7  | 34###   |   #####
```

The result is split up into one or more ranges, depending on where the overlap
is:

- `none`: result is 1 range
- `left`: result is 2 ranges
- `middle`: result is 3 ranges
- `right`: result is 2 ranges
- `all`: result is 1 range

The way I decided to implement this is with a [generator](https://docs.python.org/3/howto/functional.html#generators)
function, which will successively `yield` all of the resulting ranges. Using
`yield from` with recursive calls like this [avoids nesting](https://pep20.org/#flat),
and in my opinion it looks pretty [beautiful](https://pep20.org/#beautiful).

First, it finds the first transformation that overlaps with the given base
range, yielding the unchanged base and returning early if there are none. Then
it yields the masked segment, the results of transforming the unmasked left
segment (if any), and the results of transforming the unmasked right segment (if
any).

```py title="2023\day05\solution.py"
def transform_range(
        base: range,
        transformations: list[Transformation],
) -> Generator[range]:
    for mask, offset in transformations:
        # If this range overlaps with base, use its mask and offset
        if base.start < mask.stop and mask.start < base.stop:
            break
    else:
        # If no mask overlapped with base, yield only the unchanged base
        yield base
        return

    # Apply transformation to segment within mask
    start = max(base.start, mask.start)
    stop = min(base.stop, mask.stop)
    yield range(start + offset, stop + offset)
    # Apply transformations to segment before mask
    if base.start < mask.start:
        yield from transform_range(
            range(base.start, mask.start),
            transformations,
        )
    # Apply transformations to segment after mask
    if mask.stop < base.stop:
        yield from transform_range(
            range(mask.stop, base.stop),
            transformations,
        )
```

:::tip
Yes, I indented the code correctly. In Python, the `for` loop and the `while`
loop have [an optional `else` clause](https://docs.python.org/3/tutorial/controlflow.html#else-clauses-on-loops),
which runs only if no `break` occurs.

_Without_ the `for`..`else` clause, the code might look something like this:

```py {1,5,7-8}
overlap_was_found = False
for mask, offset in transformations:
    # If this range overlaps with base, use its mask and offset
    if base.start < mask.stop and mask.start < base.stop:
        overlap_was_found = True
        break
if overlap_was_found:
    pass
else:
    # If no mask overlapped with base, yield only the unchanged base
    yield base
    return
```

However, not using an extra flag variable makes the code [more simple](https://pep20.org/#simple).
:::

With this function in hand, Part 2 proceeds much like Part 1, but with
transformations being applied to many ranges instead of one number.

```py title="2023\day05\solution.py" ins={9-11,13-18,20}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        transformation_groups = [parse_transformations(b) for b in blocks]
        location_ranges: list[range] = []
        for seed_range in seed_ranges:
            ranges = [seed_range]
            for transformations in transformation_groups:
                ranges = [
                    result
                    for r in ranges
                    for result in transform_range(r, transformations)
                ]
            location_ranges.extend(ranges)

        return min(r.start for r in location_ranges)
```

To get the minimum location number this time, we want to find the `min` of the
starting values of all the location ranges. Now we're done, and my computer
didn't freeze this time!
