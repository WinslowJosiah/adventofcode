---
year: 2024
day: 3
title: "Mull It Over"
slug: 2024/day/3
pub_date: "2026-04-11"
# concepts: [regex]
---
## Part 1

We're looking through a corrupted computer program for strings that look like
instructions. This is a perfect use case for [regular expressions](https://docs.python.org/3/howto/regex.html)!

A regular expression, or "regex", can be used to search a string for substrings
that match a given pattern. In this case, that pattern is "looks like a `mul()`
instruction" -- things like `mul(44,46)` or `mul(123,4)`. We'll also want to
save the number parts, so we can multiply them together; the way we do that in
regex is with "capturing groups".

Here are all the parts of a `mul()` instruction, along with how they are
represented in a regex:

- `mul\(`: The literal characters `mul(`. (The `(` character must be escaped, as
it has special meaning in regexes.)
- `(\d{1,3})`: One to three (`{1,3}`) digit characters (`\d`), saved in a
"capturing group" (`(...)`).
- `,`: A literal comma.
- `(\d{1,3})`: Another set of one to three digit characters, saved in another
capturing group.
- `\)`: The literal character `)` (which also must be escaped).

The resulting regex is `mul\((\d{1,3}),(\d{1,3})\)`. If you want, you can test
out this regex [here on regex101](https://regex101.com/r/ZQGUG5/1) and see
exactly how it works; you'll notice that all of the `mul()` instructions will be
matched, and nothing else.

Once we find all the `mul()` instructions, we'll want to multiply the two
numbers in each instruction, and add up all the products. This becomes
surprisingly simple with our regex in hand; we can just use [`re.findall`](https://docs.python.org/3/library/re.html#re.findall)
to find all matches of our regex, and `sum` up the results of multiplying the
numbers.

```py title="2024\day03\solution.py"
import re

class Solution(TextSolution):
    def part_1(self) -> int:
        return sum(
            int(a) * int(b)
            for a, b in re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", self.input)
        )
```

Very manageable, especially if you're already familiar with regex.

## Part 2

Turns out there are some _more_ instructions we should be looking for in the
corrupted program: `do()` and `don't()`. They don't change what counts as a
`mul()` instruction -- only _which_ instructions to include in our total or not
-- so let's factor out our `mul()`-totaling code into a function.

```py title="2024\day03\solution.py" ins={3-7,15} ins=/(program)\\)/
import re

def get_mul_total(program: str) -> int:
    """
    Get the sum of the `mul()` commands in a program. `do()` and
    `don't()` commands are ignored; only the `mul()` commands are done.
    """
    return sum(
        int(a) * int(b)
        for a, b in re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", program)
    )

class Solution(TextSolution):
    def part_1(self) -> int:
        return get_mul_total(self.input)
```

What we have to do now is distinguish which segments of the program to _do_ and
which segments to _not_ do, and calculate our answer for only those segments
that we want to _do_. Believe it or not, we can also do this using regular
expressions![^real-world-context]

[^real-world-context]: Normally, by using regexes for this kind of thing, we'd
be [making a _huge_ mistake](https://stackoverflow.com/a/1732454).

    In a real-world context, what we _should_ be using is some sort of tokenizer
    and parser; I would recommend the book [Crafting Interpreters](https://craftinginterpreters.com/)
    by Robert Nystrom if you're interested in how a more complex real-world
    programming language is interpreted.

    But for this ultra-simplified example, using regexes is good enough.

This time, we'll want the regex to match everything between a `do()` and
`don't()` instruction. We'll also want to make sure the very start of the string
is treated as a `do()` and the very end of the string is treated as a `don't()`,
so we don't miss instructions near the start and end. The resulting regex will
be a bit complex, so let's break it down into parts:

1. The start of the string, or a `do()` instruction.

    The way to match the start of the string is `^`, and the way to match one of
    several possible patterns is by putting `|` in between them. So this part of
    the pattern would be `^|do\(\)`.
2. Whatever's in between.

    The usual way to match zero or more characters is with `.*`. However, `*`
    is a _greedy_ quantifier -- it matches as much text as possible -- which is
    not the behavior we want. Instead, we can use the _lazy_ quantifier `*?`,
    which does the same as `*`, except it matches as _little_ text as possible.
    So this part of the pattern would be `.*?`.
3. A `don't()` instruction, or the end of the string.

    The way to match the end of the string is `$`. So this part of the pattern
    would be `don't\(\)|$`.

Putting it all together, we have the three parts of our regex (written here in
"verbose" form, where whitespace and comments are ignored):

```regex
(?:^|do\(\))     # start of input, or do()
(.*?)            # whatever's in between (lazily)
(?:don't\(\)|$)  # don't(), or end of input
```

I've placed the second part in a capturing group (`(...)`) because we need its
contents, and I've placed the first and third parts in _non_-capturing groups
(`(?:...)`) because we _don't_ need their contents. If you try out this regex
[here on regex101](https://regex101.com/r/PiT4LE/1), you'll see that only the
segments of the input that we should "do" are matched.

The hard part of writing the regex is over, and now we can simply `sum` over all
matches.

```py title="2024\day03\solution.py" {8-10}
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        segments_to_do = re.findall(
            r"""
                (?:^|do\(\))     # start of input, or do()
                (.*?)            # whatever's in between (lazily)
                (?:don't\(\)|$)  # don't(), or end of input
            """,
            self.input,
            flags=re.DOTALL | re.VERBOSE,
        )
        return sum(get_mul_total(segment) for segment in segments_to_do)
```

:::attention
When writing longer/more complex regexes, it's often helpful to write them in
"verbose" form, where whitespace and comments are ignored, as I did above. But
keep in mind that this requires you to pass in the `re.VERBOSE` flag.

I also pass the `re.DOTALL` flag to make the `.` character match any character
at all, including a newline; without it, `.` would match any character _except_
a newline.
:::

If there were a Part 3 to this puzzle, I would _definitely_ switch to another
non-regex approach. But I thought this was a good opportunity to demonstrate the
power of regular expressions.
