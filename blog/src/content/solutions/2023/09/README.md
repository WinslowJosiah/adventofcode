---
year: 2023
day: 9
title: "Mirage Maintenance"
slug: 2023/day/9
pub_date: "2025-10-17"
# concepts: [recursion]
---
## Part 1

This puzzle doesn't really call for much; after parsing the input as a list of
value histories (i.e. a list of lists of `int`s), the only thing left to do is
`sum` up extrapolated values for each history.

```py title="2023\day09\solution.py" "extrapolate"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        histories = [list(map(int, line.split())) for line in self.input]
        return sum(extrapolate(h) for h in histories)
```

The only thing that's missing is the `extrapolate` function itself, but it
doesn't call for much either. I'm aware of a neat formula I could use for this,[^neat-formula]
but instead I'll use a recursive definition.

[^neat-formula]: I saw [this solution by `u/1str1ker1` on Reddit](https://reddit.com/comments/18e5ytd/comment/kdedoed)
that uses the following formula, which doesn't require recursion or taking
differences:

    $$
    y_{n+1} = \sum_{k=0}^{n} y_k \binom{n+1}{k} (-1)^{n-k}
    $$

    I think it's a beautiful formula, but I don't quite understand how it works.

- **Base case**: If all the values are 0, the result will be 0.
- **Recursive case**: If we extrapolate the _differences_, we get the difference
between the latest history value and the value that would come next. So the
result will be the latest history value plus the extrapolated difference.

`not any(history)` is a neat shorthand for checking if `history` contains all
0s,[^any-truthy] and [`itertools.pairwise`](https://docs.python.org/3/library/itertools.html#itertools.pairwise)
loops through the pairs of history values so we can gather their differences.

[^any-truthy]: This is because `any` checks whether any items in an iterable are
[considered "true"](https://docs.python.org/3/library/stdtypes.html#truth-value-testing),
and 0 is considered "false".

```py title="2023\day09\solution.py"
from itertools import pairwise

def extrapolate(history: list[int]) -> int:
    if not any(history):
        return 0
    diffs = [b - a for a, b in pairwise(history)]
    return history[-1] + extrapolate(diffs)
```

Short and sweet!

## Part 2

Although it seems like we'd need to rewrite our `extrapolate` function to also
extrapolate backwards, we don't need to. We can just reverse the history list
before we pass it to `extrapolate`! (After all, moving backwards is basically
moving forwards, but in reverse... if that makes sense.)

```py title="2023\day09\solution.py" ins=/def (_solve)/ ins=", reverse: bool" ins="h[::-1] if reverse else " ins={9,11-12}
...

class Solution(StrSplitSolution):
    def _solve(self, reverse: bool) -> int:
        histories = [list(map(int, line.split())) for line in self.input]
        return sum(extrapolate(h[::-1] if reverse else h) for h in histories)

    def part_1(self) -> int:
        return self.solve(reverse=False)

    def part_2(self) -> int:
        return self.solve(reverse=True)
```

:::tip
A common idiom for reversing a list `s` in Python is `s[::-1]` -- that is,
getting values from one end to the other, stepping by -1 each time.

Lists also have a [`reverse`](https://docs.python.org/3/library/stdtypes.html#sequence.reverse)
method (called like `s.reverse()`), but it operates in-place and returns `None`;
on the other hand, `s[::-1]` returns a reversed copy of the list.

If you simply need to iterate over the items of `s` in reverse order,
[`reversed(s)`](https://docs.python.org/3/library/functions.html#reversed)
should be used instead, as it neither modifies the list nor copies it.
:::

And just like that, we're already done! I'm surprised we could get away with so
little code.
