---
year: 2025
day: 3
title: "Lobby"
slug: 2025/day/3
pub_date: "2025-12-03"
# concepts: [recursion]
---
## Part 1

Part 1 today feels a bit easy -- almost _too_ easy.

[`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
can be used to get all possible pairs of batteries, in the same order as they
are in the input. So to get the maximum "joltage" level for a bank of batteries,
we _could_ just get the `max` of all the combinations of 2 batteries, then join
them into a single string with `"".join(...)`.

```py title="2025\day03\solution.py"
from itertools import combinations

def max_joltage(bank: str) -> str:
    return "".join(max(combinations(bank, 2)))
```

:::tip
In most scenarios where you're treating a number as a series of digits instead
of as a mathematical quantity, it's better to represent it as a `str` instead of
an `int`. As a rule of thumb, if it doesn't make sense to add 1 to a number or
multiply it by 2, it should probably be a string.

In this case, I chose to make each joltage level a `str` because they're made by
literally placing digits side by side.
:::

Then we can simply `sum` over the max joltage of each line of our input --
remembering to convert our joltage strings to `int`s so we can add them
together.

```py title="2025\day03\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(int(max_joltage(line)) for line in self.input)
```

That's a pretty quick brute-force solution. But I'm guessing we won't be able to
brute-force Part 2 in the same way.

## Part 2

My suspicions were correct.

Sure, you _could_ just replace the `2` with a `12` for Part 2... but you won't
get a result very quickly.

```py title="2025\day03\solution.py" ins=", batteries: int" ins=/bank(, batteries)/ ins=/, batteries=\d+/
from itertools import combinations

def max_joltage(bank: str, batteries: int) -> str:
    return "".join(max(combinations(bank, batteries)))

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(int(max_joltage(line, batteries=2)) for line in self.input)

    def part_2(self) -> int:
        return sum(int(max_joltage(line, batteries=12)) for line in self.input)
```

So let's think a little harder about what we're doing. We're trying to get a
combination of some number of digits from our battery bank, to make the highest
number possible. Let's think about this recursively and see if that helps.

The simplest case I can think of is where we're trying to get the max joltage
with a single battery. Obviously, the max joltage will be whatever the highest
battery value is.

- **Base case**: If we can turn on only 1 battery, the result will be the
maximum value of any battery in the bank.

And in the case of even more batteries, the most important thing is that the
first battery's value should be as high as possible; for example, _any_ joltage
level starting with a `9` will be higher than even the highest joltage level
starting with an `8` or lower.

So in the case of two batteries, the first battery will be the highest-valued
battery anywhere in the bank -- except for the last battery slot, because
nothing could go after it. In general, in the case of $n$ batteries, the first
battery will be the highest-valued battery anywhere except the last $n - 1$
slots. From here, we can use recursion to find the result for the remaining
$n - 1$ batteries.

- **Recursive case**: If we can turn on $n$ batteries, the first battery's value
will be the maximum value of any battery in the bank (excluding the final
$n - 1$ batteries). So the result will be that first battery, concatenated with
the maximum joltage level for the _remaining_ section of the bank using $n - 1$
batteries.

We can implement this rather straightforwardly.

- `max(bank)` is all we need for the base case.
- We can use "slicing" to retrieve only certain portions of the battery bank.
`bank[:-n]` gets everything in `bank` from the start up to (but not including)
the `n`th element from the end, and `bank[n:]` gets everything in `bank` from
the `n`th element from the start all the way to the end. We'll need these, as
well as [`str.index`](https://docs.python.org/3/library/stdtypes.html#str.index)
(for getting the first digit's index), to implement the recursive case.

```py title="2025\day03\solution.py" del={1} ins={"Base case":4-7} ins={"Recursive case":9-15}
from itertools import combinations

def max_joltage(bank: str, batteries: int) -> str:

    # The max joltage with a single battery is the bank's highest digit
    if batteries == 1:
        return max(bank)


    # Find highest first digit (leaving enough space for the rest of the
    # batteries)
    first_digit = max(bank[: -(batteries - 1)])
    # Combine that digit with the max joltage for the rest of the bank
    i = bank.index(first_digit)
    return first_digit + max_joltage(bank[i + 1 :], batteries - 1)
```

With this new `max_joltage` function, the solution becomes extremely fast -- not
to mention, we've eliminated the need for `itertools.combinations`!
