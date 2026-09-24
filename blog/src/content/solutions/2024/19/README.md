---
year: 2024
day: 19
title: "Linen Layout"
slug: 2024/day/19
pub_date: "2026-09-24"
# concepts: [recursion]
---
## Part 1

The staff at the onsen will let us in for free if we can arrange their towels.
Not a bad deal; let's see how well we can do.

Before we start, we need to know what towels we're working with, and what
designs we're allowed to make with them. The input is in the form of two
"blocks" separated by two newlines, and they're easy to parse into a list of
towels and a list of designs.

```py title="2024\day19\solution.py"
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_towels, raw_designs = self.input
        towels = raw_towels.split(", ")
        designs = raw_designs.splitlines()
        ...
```

Now, which of these designs can we make with our towels? Instead of using some
sort of brute-force method, let's see if we can think about this _recursively_.
(To show what I mean, I'll be using the towels from the sample input: `r`, `wr`,
`b`, `g`, `bwu`, `rb`, `gb`, and `br`.)

For our **recursive case**, we can start by thinking about which of our towels
could go _first_ in our arrangement -- i.e. which of our towels' stripe patterns
the design _starts with_. If we couldn't put any of our towels first, the design
is _not_ possible; otherwise, we'll want to check whether or not the _rest_ of
the design is possible. So for example:

- If the design is `brwrr`:
    - We could start with a `b` towel, and check whether `rwrr` is possible.
    - We could start with a `br` towel, and check whether `wrr` is possible.
- If the design is `bggr`:
    - We could start with a `b` towel, and check whether `ggr` is possible.
- If the design is `gbbr`:
    - We could start with a `g` towel, and check whether `bbr` is possible.
    - We could start with a `gb` towel, and check whether `br` is possible.
- If the design is `rrbgbr`:
    - We could start with a `r` towel, and check whether `rbgbr` is possible.
- If the design is `ubwu`:
    - This design is _impossible_; none of the towels we have available could go
    first in our arrangement.
- If the design is `bwurrg`:
    - We could start with a `b` towel, and check whether `wurrg` is possible.
    - We could start with a `bwu` towel, and check whether `rrg` is possible.
- If the design is `brgr`:
    - We could start with a `b` towel, and check whether `rgr` is possible.
    - We could start with a `br` towel, and check whether `gr` is possible.
- If the design is `bbrgwb`:
    - We could start with a `b` towel, and check whether `brgwb` is possible.[^not-yet-impossible]

[^not-yet-impossible]: It turns out that `brgwb` is _not_ possible, but at this
point in the process, we don't _know_ that yet.

We also need to figure out a **base case**, which will answer the simplest
possible version of our question. In this case, the simplest possible case I can
imagine is the case of an _empty_ design -- a design with no stripes -- which we
will say is _possible_.

:::note
Yes, an "empty design" sounds a bit abstract, but think about it; if we're ever
asking ourselves "is this design valid?" about an empty string, it means we've
found a towel arrangement that fits the _entire_ design from start to finish,
and we're asking if the "rest" of it is possible.

As a concrete example, let's say we're asking if `b` is a possible design.
Obviously, we can try placing a `b` towel first, and then our recursive case
requires us to ask whether the "rest" of this design is possible. But there is
no "rest" of the design; there are _no stripes_ left to match, and we've in fact
matched _every_ stripe of the design at this point. So it makes sense to say
here that the "empty design" _is possible_ -- and thus, `b` is possible.
:::

:::tip
Sometimes in a recursive problem, the base cases can get a bit abstract, and it
can be tough to think of what their answers should be; the [factorial of zero](https://en.wikipedia.org/wiki/Factorial#Factorial_of_zero)
is a good example of this. In cases like this, it can help to trace out the
recursive steps down to the lowest level _knowing_ what you want the ultimate
result to be, and simply make the choice that _gives_ you that ultimate result.
:::

Now that we have our recursive case and base case, we can easily implement a
function to validate each design -- returning `True` if the design is valid, and
`False` otherwise. And thanks to the fact that [`bool`s act like `int`s](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)
when you add them together, we can simply add up our `True`/`False` results
directly with `sum` to count how many designs are possible.

```py title="2024\day19\solution.py" ins={1,11-24}
from functools import cache

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_towels, raw_designs = self.input
        towels = raw_towels.split(", ")
        designs = raw_designs.splitlines()

        @cache
        def validate_design(design: str) -> bool:
            # An empty design (with no stripes) is possible
            if not design:
                return True
            # For each towel that could go first, check the validity of
            # the rest of the design
            return any(
                validate_design(design.removeprefix(towel))
                for towel in towels
                if design.startswith(towel)
            )

        return sum(validate_design(design) for design in designs)
```

:::tip
The `@cache` line I added above the `validate_design` function is a [decorator](https://docs.python.org/3/glossary.html#term-decorator)
-- something you can place atop a function's definition to change how it
behaves. In this case, decorating a function with [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache)
will _cache_ its outputs; that way, calling it multiple times with the same
arguments will only calculate the answer _once_ and reuse it each time, saving
time on repeated calls. It's needed badly for the full puzzle input!
:::

## Part 2

Looks like the onsen staff don't know good towel arrangements when they see
them. So at this point, let's do the lowest-effort thing possible, and write
some code to find all possible towel arrangements; the designs will be _their_
responsibility from now on.

Believe it or not, we don't have to change very much from our Part 1 solution.
The same recursive algorithm that checks the existence of valid towel
arrangements can also be used to _count_ those arrangements, with two tweaks:

- Instead of `return True` in our base case, we'll `return 1` to signify that we
can make the design using a _single_ towel arrangement.
- Instead of `any` in our recursive case, we'll use `sum` to add up the towel
arrangement counts for each possible starting towel.

```py title="2024\day19\solution.py" del={12,17,21,23,29} ins={13,18,22,24,30}
from functools import cache

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_2(self) -> int:
        raw_towels, raw_designs = self.input
        towels = raw_towels.split(", ")
        designs = raw_designs.splitlines()

        @cache
        def validate_design(design: str) -> int:
        def count_arrangements(design: str) -> int:
            # An empty design (with no stripes) can be made in one way
            # (by using no towels)
            if not design:
                return True
                return 1
            # For each towel that could go first, count the possible
            # towel arrangements for the rest of the design
            return any(
            return sum(
                validate_design(design.removeprefix(towel))
                count_arrangements(design.removeprefix(towel))
                for towel in towels
                if design.startswith(towel)
            )

        return sum(validate_design(design) for design in designs)
        return sum(count_arrangements(design) for design in designs)
```

In fact, we can turn this into a unified `solve` function by making a useful
observation: a design is valid _if and only if_ the number of towel arrangements
that can make it is nonzero. This means that, if we have our Part 1 answer count
the number of nonzero results of `count_arrangements`, we could get rid of the
`validate_design` function entirely.

My unified function first calculates the number of towel arrangements for each
design, and stores these counts in a list called `arrangements`. The answers for
both parts are the result of two simple `sum()` expressions:

1. For Part 1, first I use `map(bool, arrangements)` to convert the arrangement
counts to `bool`s; this makes the nonzero values `True` and the zero values
`False`. Then, I can pass these `bool`s to `sum()` to count the valid designs.
2. For Part 2, I can just pass `arrangements` to `sum()` directly to count the
valid arrangements.

```py title="2024\day19\solution.py" ins="solve" ins="tuple[int, int]" ins={25-28}
from functools import cache

class Solution(StrSplitSolution):
    separator = "\n\n"

    def solve(self) -> tuple[int, int]:
        raw_towels, raw_designs = self.input
        towels = raw_towels.split(", ")
        designs = raw_designs.splitlines()

        @cache
        def count_arrangements(design: str) -> int:
            # An empty design (with no stripes) can be made in one way
            # (by using no towels)
            if not design:
                return 1
            # For each towel that could go first, count the possible
            # towel arrangements for the rest of the design
            return sum(
                count_arrangements(design.removeprefix(towel))
                for towel in towels
                if design.startswith(towel)
            )

        arrangements = [count_arrangements(design) for design in designs]
        # Part 1 counts designs with a nonzero number of arrangements;
        # Part 2 counts all arrangements for all designs
        return sum(map(bool, arrangements)), sum(arrangements)
```

Excellent towel-arranging work, if I do say so myself. We _deserve_ that free
entry into the onsen.
