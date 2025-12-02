---
year: 2025
day: 2
title: "Gift Shop"
slug: 2025/day/2
pub_date: "2025-12-02"
# concepts: [regex]
---
## Part 1

It's a good day to use a [`range`](https://docs.python.org/3/library/stdtypes.html#typesseq-range).
We can iterate through those to get each product ID.

In fact, because we're given _many_ ranges, and we want to test each number from
all of them, let's write a function that will `yield from` all of the ranges in
the input. (I find that using `yield from` helps keep my nesting nice and [flat](https://pep20.org/#flat).)

```py title="2025\day02\solution.py"
from collections.abc import Iterator

def iter_ranges(raw_ranges: list[str]) -> Iterator[int]:
    for raw_range in raw_ranges:
        start, stop = map(int, raw_range.split("-"))
        # NOTE The stop of the input range is inclusive.
        yield from range(start, stop + 1)
```

We want to filter these product IDs to the ones that fit a certain pattern --
namely, "is some string followed by another copy of that string". This sounds
like a job for a [regular expression](https://docs.python.org/3/howto/regex.html)
(aka "regex"); let's try to create one that matches the pattern we're looking
for.

If you want a regex pattern to refer to a previously-matched part of the
pattern, you'll want to use backreferences. For example, `\1` will match the
contents of the first capturing group, `\2` will match the second group, `\3`
will match the third, and so on. This can easily be used to find adjacent
repetitions in a string; here are two examples, one that finds repeats of any
single character, and one that finds repeats of any (nonzero) amount of
characters.

```py
>>> import re
>>> re.finditer(r"(.)\1", "coffee table book")
[<re.Match object; span=(2, 4), match='ff'>,
 <re.Match object; span=(4, 6), match='ee'>,
 <re.Match object; span=(14, 16), match='oo'>]
>>> re.finditer(r"(.+)\1", "better repetition stringing")
[<re.Match object; span=(2, 4), match='tt'>,
 <re.Match object; span=(11, 15), match='titi'>,
 <re.Match object; span=(21, 27), match='inging'>]
```

If we want the pattern to only match if the _whole_ string matches, we can
prefix it with `^` and suffix it with `$`. Let's combine all of this to make a
regex:

- `^`: The beginning of the string.
- `(.+)`: One or more (`+`) of any character (`.`), saved in a "capturing group"
(`(...)`).
- `\1`: Whatever was in that capturing group, again.
- `$`: The end of the string.

The resulting regex is `^(.+)\1$`, which will match any string that consists of
some sequence of characters repeated twice. Our approach will be to convert
every product ID to a string and check whether this regex matches; you can see
the result of doing this on the sample input [here on regex101](https://regex101.com/r/GGMn5K/1).

```py
>>> import re
>>> pattern = re.compile(r"^(.+)\1$")
>>> words = ["nana", "popo", "zigzag", "bonbon", "hahaha"]
>>> [word for word in words if pattern.match(word)]
["nana", "popo", "bonbon"]
```

:::tip
If a regex pattern is being used repeatedly, it's good practice to compile it
first with [`re.compile`](https://docs.python.org/3/library/re.html#re.compile).
That way, the pattern object is only created once.
:::

We can easily use this to sum all numbers `n` where `str(n)` matches the regex
pattern. (My template, which is based on [David Brownman's template](https://github.com/xavdid/advent-of-code-python-template),
allows me to automatically split the input by a separator; you may want to call
`str.split` on your input explicitly.)

```py title="2025\day02\solution.py"
import re
...

class Solution(StrSplitSolution):
    separator = ","

    def part_1(self) -> int:
        pattern = re.compile(r"^(.+)\1$")
        return sum(
            n
            for n in iter_ranges(self.input)
            if pattern.match(str(n))
        )
```

Regexes are powerful, aren't they?

## Part 2

More repetition! More repetition! More repetition!

This time, the repeating sequence of digits could be repeated _twice or more_,
not just twice exactly. And in fact, there's a _single_ change we can make to
our regex to solve this one, which I've marked in bold below:

- `^`: The beginning of the string.
- `(.+)`: One or more (`+`) of any character (`.`), saved in a "capturing group"
(`(...)`).
- `\1+`: Whatever was in that capturing group, again, **repeated one or more
times (`+`)**.
- `$`: The end of the string.

The only change is adding `+` after the backreference -- an addition of a single
character! This ensures that more repetitions of the backreference after the
second one are detected.

The resulting pattern is `^(.+)\1+$`, which you can test [here on regex101](https://regex101.com/r/RmFF5k/1).

```py
>>> import re
>>> pattern = re.compile(r"^(.+)\1+$")
>>> words = ["nana", "popo", "zigzag", "bonbon", "hahaha"]
>>> [word for word in words if pattern.match(word)]
["nana", "popo", "bonbon", "hahaha"]
```

Other than the choice of pattern, the logic of the two parts is exactly the
same. So we can factor it out into a `_solve` function that can do either part,
depending on an option that is passed to it.

```py title="2025\day02\solution.py" ins=/def (_solve)/ ins=", at_least_twice: bool" ins=/pattern = re\\.compile\\((.*else ).*\\)/ ins={15,18}
...

class Solution(StrSplitSolution):
    separator = ","

    def _solve(self, at_least_twice: bool) -> int:
        pattern = re.compile(r"^(.+)\1+$" if at_least_twice else r"^(.+)\1$")
        return sum(
            n
            for n in iter_ranges(self.input)
            if pattern.match(str(n))
        )

    def part_1(self) -> int:
        return self._solve(at_least_twice=False)

    def part_2(self) -> int:
        return self._solve(at_least_twice=True)
```

I'll admit, my first thought here actually _wasn't_ to use regexes; my initial
solution used [`itertools.batched`](https://docs.python.org/3/library/itertools.html#itertools.batched)
to break up each product ID string into batches manually. But using regexes made
this solution much easier _and_ faster!

Regexes are a good problem-solving tool to have in your back pocket (so long as
you don't give yourself [more problems](https://xkcd.com/1171)).
