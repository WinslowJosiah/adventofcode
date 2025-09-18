---
year: 2023
day: 1
title: "Trebuchet?!"
slug: 2023/day/1
pub_date: "2025-10-07"
# concepts: [regex]
---
Hello, World!

Welcome to my Advent of Code solution blog! 2023 was my first year participating
in Advent of Code (even though I'm writing this explanation years later). At the
time, I didn't have as robust a solution template to work with, so I've
rewritten my solutions to make better use of the template I use now (a slightly
modified version of [David Brownman's template](https://github.com/xavdid/advent-of-code-python-template)).

My original 2023 solutions were a bit clunky in general, so the ones I felt were
_too_ clunky to adapt here will be modelled after [David Brownman's solutions](https://advent-of-code.xavd.id/writeups/2023)
instead. I'd encourage you to check them out as well.

With that out of the way, let's get started!

## Part 1

We're asked to recover corrupted calibration values for a trebuchet. For each
line of the input, we need the first digit and last digit of the line,
interpreted as a single number.

Let's write a function that gets the calibration value for a line.
[`str.isdigit`](https://docs.python.org/3/library/stdtypes.html#str.isdigit)
will help us get only the digit characters of the line. Then we can concatenate
the first and last digit character to get a two-character string, and convert
that string to an `int`.

```py title="2023/day01/solution.py"
def get_calibration(line: str) -> int:
    digits = [c for c in line if c.isdigit()]
    return int(digits[0] + digits[-1])
```

The puzzle asks for the sum of these calibration values, so all we need to do is
call our function on each line of the input, and get the `sum`.

```py title="2023/day01/solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(get_calibration(line) for line in self.input)
```

## Part 2

Now we're asked to look at not just the digits, but the digit _words_ as well.
Otherwise, the calibration values are calculated as normal (with the words being
converted to their digits, of course).

An obvious choice here would be to use [regular expressions](https://docs.python.org/3/howto/regex.html)
(aka "regexes"). Regexes are useful for finding substrings that match a given
pattern, and a pattern like "looks like a digit or digit word" certainly
qualifies. However, we do have to be careful.

We might naively create a pattern that simply matches any of the digits or
words, and find every match using [`re.findall`](https://docs.python.org/3/library/re.html#re.findall).
(You can test one such pattern [here on regex101](https://regex101.com/r/TI7s6z/1).)

But watch what happens with the line `eightwothree` (from the sample input).
We'd expect to find the "digits" `['eight', 'two', 'three']`, but here's what we
find instead:

```py
>>> import re
>>> pattern = r"1|2|3|4|5|6|7|8|9|one|two|three|four|five|six|seven|eight|nine"
>>> line = "eightwothree"
>>> re.findall(pattern, line)
['eight', 'three']
```

It skipped over the `two`![^right-answer] This is because `re.findall` returns
only the _non-overlapping_ matches; once `eight` is found, it searches for other
matches in the `wothree` part, skipping over where the `two` would begin.

[^right-answer]: In this case (and for all other lines in the sample input), our
calibration calculation would still have given us the right answer. But the full
puzzle input will have _many_ cases where this discrepancy steers us wrong.

How do we fix this? The way I came up with is to use a [lookahead assertion](https://docs.python.org/3/howto/regex.html#lookahead-assertions).
If your regex pattern looks like `(?=...)` (where `...` is another pattern), it
will be matched if the current location is followed by the contained pattern,
_without actually moving forward_.

This means we can rewrite our pattern as a lookahead assertion; we will match
any position of the input string followed by a digit or word, and it will _act_
like a series of overlapping matches! We just have to remember to put the
digit/word in a group (i.e. `(...)`), or else it won't be accessible. (You can
test this modified pattern [here on regex101](https://regex101.com/r/EHQqUo/1).)

```py
>>> import re
>>> pattern = r"(?=(1|2|3|4|5|6|7|8|9|one|two|three|four|five|six|seven|eight|nine))"
>>> line = "eightwothree"
>>> re.findall(pattern, line)
['eight', 'two', 'three']
```

Now we get the expected result.

---

First, let's define a mapping between the words and the digits they represent:

```py title="2023/day01/solution.py"
DIGITS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
```

Next, let's redefine `get_calibration` to find all occurrences of a regex. We
can build the regex dynamically to save some repetition.

```py title="2023/day01/solution.py" ins={1-2,7-13} ins=", include_spelled: bool"
import re
from typing import cast

...

def get_calibration(line: str, include_spelled: bool) -> int:
    VALID_DIGITS = list(DIGITS.values())
    if include_spelled:
        VALID_DIGITS.extend(DIGITS.keys())
    # NOTE The regex will look something like /(?=(a|b|c|d))/, which
    # uses positive lookahead to find any point in the line immediately
    # followed by a valid digit (and captures that digit).
    DIGIT_REGEX = rf"(?=({"|".join(VALID_DIGITS)}))"
    ...
```

Finally, we can use `re.findall` to get our matches, and
`DIGITS.get(match, match)` as a succinct way to convert the words into digits.[^typing-cast]

[^typing-cast]: For whatever reason, Pyright (the static type checker I use)
infers the type of `match` as `Any`. Using `typing.cast` to "cast" it to `str`
lets the type checker know that the string-like things I do to it later are
indeed legal.

```py title="2023/day01/solution.py" ins={3-6}
def get_calibration(line: str, include_spelled: bool = False) -> int:
    ...
    digits = [
        DIGITS.get(match, cast(str, match))
        for match in re.findall(DIGIT_REGEX, line)
    ]
    ...
```

Running this new function for Part 2 will then give us the correct answer.

```py title="2023/day01/solution.py" ins=", include_spelled=False" ins=", include_spelled=True"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(
            get_calibration(line, include_spelled=False) for line in self.input
        )

    def part_2(self) -> int:
        return sum(
            get_calibration(line, include_spelled=True) for line in self.input
        )
```

Bit of a rough first day, in my opinion. But regexes at least get the job done.
