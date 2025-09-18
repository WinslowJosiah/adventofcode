---
year: 2023
day: 15
title: "Lens Library"
slug: 2023/day/15
pub_date: "2025-10-27"
# concepts: []
---
## Part 1

So we're doing some math on ASCII values. We'll need to use [`ord`](https://docs.python.org/3/library/functions.html#ord)
to get the ASCII value of a character; with this in hand, we can just do exactly
what it says in the prompt.

```py title="2023\day15\solution.py"
def holiday_hash(st: str) -> int:
    result = 0
    for c in st:
        result += ord(c)
        result *= 17
        result %= 256
    return result

class Solution(StrSplitSolution):
    separator = ","

    def part_1(self) -> int:
        return sum(map(holiday_hash, self.input))
```

:::tip
Instead of using a generator expression within the `sum`, I use the [`map`](https://docs.python.org/3/library/functions.html#map)
function.

`map(function, iterable)` will take each `item` from `iterable`, and yield
`function` applied to the `item` one by one. It'd be the same as writing
`(function(item) for item in iterable)`, and it's sometimes more convenient.
:::

## Part 2

This puzzle really reminded me of my Data Structures and Programming course in
college. If you're not aware, the :abbr[HASHMAP]{title="Holiday ASCII String Helper Manual Arrangement Procedure"}
described by the prompt is one way to implement a **hash map**[^separate-chaining]
-- the Python equivalent of which would be a `dict` -- and the :abbr[HASH]{title="Holiday ASCII String Helper"}
algorithm from Part 1 is its **hash** function!

[^separate-chaining]: Specifically, it describes a hash map where collision
resolution is done by [separate chaining](https://en.wikipedia.org/wiki/Hash_table#Separate_chaining).
Look into it, if you're into that sort of thing!

And in fact, specifically because we're using Python, it's convenient here to
use `dict`s to represent our boxes of lenses. As of Python 3.7, `dict`s preserve
insertion order[^cpython-3-6] -- which is exactly the behavior we want our boxes
of lenses to have.

[^cpython-3-6]: Technically this behavior existed in Python 3.6, but only as an
implementation detail of CPython 3.6 -- the default and most widely used
implementation of Python. Python 3.7 made this behavior _official_.

The order of the boxes themselves within the line of boxes doesn't matter for
the answer, so we can use a `defaultdict` instead of a `list` to make our lives
a bit easier. So our line of lens boxes will be a `defaultdict` of `dict`s
(which themselves map `str` labels to `int` focal lengths).

The code for parsing the input and updating the lenses is simple from here.

```py title="2023\day15\solution.py"
from collections import defaultdict

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        boxes: dict[int, dict[str, int]] = defaultdict(dict)
        for step in self.input:
            # If step looks like "abc-"
            if "-" in step:
                label = step[:-1]
                boxes[holiday_hash(label)].pop(label, None)
            # If step looks like "abc=6"
            elif "=" in step:
                label, val_str = step.split("=")
                boxes[holiday_hash(label)][label] = int(val_str)
            else:
                raise ValueError(f"unrecognized step: {step}")
```

Doing a `sum` over a nested generator gives us our answer. (Note that I add 1 to
the `box_id` and `lens_pos`, because I want their indices starting from 1
instead of 0.)

```py title="2023\day15\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        return sum(
            (box_id + 1) * (lens_pos + 1) * focal_length
            for box_id, box in boxes.items()
            for lens_pos, focal_length in enumerate(box.values())
        )
```

Today definitely wasn't as hard as I thought it'd be, but that's probably
because of Python's `dict` behavior being so convenient. I would imagine that
some more code would be required in any other language.
