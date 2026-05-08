---
year: 2024
day: 7
title: "Bridge Repair"
slug: 2024/day/7
pub_date: "2026-05-08"
# concepts: [recursion]
---
## Part 1

This just in: elephants have stolen all the mathematical operators from a bunch
of equations. In other news, operators are things that _can_ be stolen... and by
_elephants_, no less! I know, it's news to me too.

Let's not think about the plausibility of the puzzle prompt and instead think
about parsing. If you get rid of the `:` character, each line is a
whitespace-separated list of numbers. With that in mind:

- We'll use [`str.replace`](https://docs.python.org/3/library/stdtypes.html#str.replace)
to replace the `:` character in each line with nothing.
- We'll use [`str.split`](https://docs.python.org/3/library/stdtypes.html#str.split)
to split the resulting line by whitespace.
- We'll use [`map`](https://docs.python.org/3/library/functions.html#map) to
apply the `int` function to every result to get a bunch of numbers.
- And finally, we'll use [extended iterable unpacking](https://peps.python.org/pep-3132)
(that `target, *numbers` syntax) to separate the numbers into the first one and
a list of the rest of them.

```py title="2024\day07\solution.py"
def process_line(line: str) -> int:
    target, *numbers = map(int, line.replace(":", "").split())
    ...
```

How do we figure out which operators are supposed to go in each equation? For
now, let's try brute-forcing every possibility, and see how far that takes us.
We can generate every possible sequence of operators using [`itertools.product`](https://docs.python.org/3/library/itertools.html#itertools.product)
and its `repeat` argument, which will look something like this:

```py
>>> from itertools import product
>>> list(product(["+", "*"], repeat=3))
[('+', '+', '+'),
 ('+', '+', '*'),
 ('+', '*', '+'),
 ('+', '*', '*'),
 ('*', '+', '+'),
 ('*', '+', '*'),
 ('*', '*', '+'),
 ('*', '*', '*')]
```

Instead of the `+` and `*` characters, however, we can use the `add` and `mul`
functions from the [`operator`](https://docs.python.org/3/library/operator.html)
module as our operators; `add(a, b)` will be the same as `a + b`, and
`mul(a, b)` will be the same as `a * b`. And the amount of operators we'll need
is `len(numbers) - 1`, so one can go in between each adjacent pair of numbers.

If evaluating these numbers with any sequence of operators results in our
target, we'll return the target so it can contribute to our grand total;
otherwise, we'll return 0.

```py title="2024\day07\solution.py" "evaluate"
from operator import add, mul

def process_line(line: str) -> int:
    target, *numbers = map(int, line.replace(":", "").split())
    ops = [add, mul]

    if any(
        evaluate(numbers, op_sequence) == target
        for op_sequence in product(ops, repeat=len(numbers) - 1)
    ):
        return target
    return 0
```

But how do we implement the `evaluate` function? There's no need to remember
:abbr[PEMDAS]{title="Python Enables My Distinctive AoC Solutions"}[^pemdas] --
each operator is applied from left to right -- so the evaluation can be done
with a fairly simple loop. We initialize a result with the leftmost number in
our number list, and update it using the next number and operator function as we
`zip` through them.

[^pemdas]: The conventional [order of operations](https://en.wikipedia.org/wiki/Order_of_operations)
is **P**arentheses, **E**xponents, **M**ultiplication and **D**ivision, and
**A**ddition and **S**ubtraction. In elementary school, my teachers called this
**PEMDAS**, and I was taught to remember it as "**P**lease **E**xcuse **M**y
**D**ear **A**unt **S**ally". This isn't a great way to learn the order of
operations for _many_ reasons... but in my opinion, the _funniest_ reason is
[this one](https://www.smbc-comics.com/comic/pemdas).

```py title="2024\day07\solution.py"
type Operator = Callable[[int, int], int]

def evaluate(numbers: list[int], op_sequence: Sequence[Operator]) -> int:
    result = numbers[0]
    for op, next_number in zip(op_sequence, numbers[1:]):
        result = op(result, next_number)
    return result
```

Processing each line and getting the `sum` gives us our answer.

```py title="2024\day07\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(process_line(line) for line in self.input)
```

The runtime isn't too bad either, at least for Part 1; it only took about 131
milliseconds on my machine. However, brute force approaches rarely ever scale
well, so Part 2 may require a different approach.

## Part 2

Now we have a new operator: concatenation! There's no builtin way in Python to
concatenate two `int`s, but we _can_ concatenate two strings with `+`. So to
create a `concat` operator function, we can convert the arguments to strings,
concatenate them, then convert the result back to an `int`.[^faster-concat]

[^faster-concat]: While I'd argue that this approach to `concat` most closely
follows [The Zen of Python](https://pep20.org/), there are other approaches that
execute faster. For example:

    ```py
    def concat(a: int, b: int) -> int:
        """Concatenate a and b; same as writing them next to each other."""
        return a * 10 ** len(str(b)) + b
    ```

    Here, `len(str(b))` is used to succinctly count the number of digits of `b`.
    An even _faster_ way to do so -- and a cursed Python snippet I absolutely
    love -- is given in [this StackOverflow answer](https://stackoverflow.com/a/74099536).
    But sadly, _none_ of this wizardry will save us from the runtime explosion
    we will soon see.

```py title="2024\day07\solution.py"
def concat(a: int, b: int) -> int:
    """Concatenate a and b; same as writing them next to each other."""
    return int(str(a) + str(b))
```

We can then include this new `concat` function in our list of operators based on
an extra argument...

```py title="2024\day07\solution.py" ins=", include_concat: bool = False" ins={4-5}
def process_line(line: str, include_concat: bool = False) -> int:
    ...
    ops = [add, mul]
    if include_concat:
        ops.append(concat)
    ...
```

...that we provide in our Part 2 solution.

```py title="2024\day07\solution.py" ins=", include_concat=True"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        return sum(
            process_line(line, include_concat=True)
            for line in self.input
        )
```

Unfortunately, the runtime has now skyrocketed from ~131 milliseconds to over 10
seconds. That's not _horrible_, but it definitely could be improved. Let's go
over a more efficient approach.

Every single number in the puzzle input is a positive integer, and every single
operation will result in a positive integer as well.[^concat-positive-integers]
This means that sometimes, a target value _can't_ be the result of an operation;
for example, you can't add `44` to anything to get `22`, you can't multiply
anything by `20` to get `192`, and you can't concatenate `5` to anything to get
`83`.[^real-numbers]

[^concat-positive-integers]: In fact, what would concatenations involving
negative numbers even _mean_? What is `100 || -13`? Would that be `10013`, or
`87` (i.e. `100-13`)? The prompt doesn't worry about it, so I won't either.

[^real-numbers]: Of course, you _could_ do all these things (except that one
concatenation) if you used real numbers. But we're working with only positive
integers.

So instead of applying the operations forwards to get to the target, we could
try starting with the target and applying the operations _backwards_. In fact,
we can turn this into a recursive algorithm, which consumes each number in the
list going backwards:

- **Base case**: If our list of numbers has only one number, the target can be
reached only if that number _is_ the target.
- **Recursive case**:
    - Extract the last number from our list of numbers.
    - If we're including the concatenation operator, and the target could be the
    result of a **concatenation** with our last number, undo the concatenation;
    then, check whether that new target can be reached by the rest of the
    numbers.
    - If the target could be the result of a **multiplication** with our last
    number, undo the multiplication; then, check whether that new target can be
    reached by the rest of the numbers.
    - If the target could be the result of an **addition** with our last number,
    undo the addition; then, check whether that new target can be reached by the
    rest of the numbers.
    - If none of these checks have succeeded, the target _cannot_ be reached.

This new approach will replace the brute-force check from before with a
recursive function I will call `is_solvable`.

```py title="2024\day07\solution.py" ins={3-4} "is_solvable"
def process_line(line: str, include_concat: bool = False) -> int:
    target, *numbers = map(int, line.replace(":", "").split())
    if is_solvable(numbers, target, include_concat):
        return target
    return 0
```

And we can implement `is_solvable` basically just as I described. First goes our
simple base case of a one-item list of numbers.

```py title="2024\day07\solution.py"
def is_solvable(
        numbers: list[int],
        target: int,
        include_concat: bool = False,
) -> bool:
    # Base case: there is only one number, so is it the target?
    if len(numbers) == 1:
        return numbers[0] == target
    ...
```

Next goes our concatenation check. [`str.endswith`](https://docs.python.org/3/library/stdtypes.html#str.endswith)
checks whether a string ends with a suffix, and [`str.removesuffix`](https://docs.python.org/3/library/stdtypes.html#str.removesuffix)
removes a suffix from the end of a string. We can convert both the target and
our last number to strings; if the stringified target ends with our stringified
last number, the target _could_ be the result of a concatenation.

```py title="2024\day07\solution.py"
def is_solvable(
        numbers: list[int],
        target: int,
        include_concat: bool = False,
) -> bool:
    ...
    *rest, last = numbers

    if include_concat:
        # Can the target be the result of a concat?
        str_last, str_target = str(last), str(target)
        if str_target.endswith(str_last):
            prefix = str_target.removesuffix(str_last)
            # NOTE We cannot concat with an empty prefix!
            if prefix and is_solvable(rest, int(prefix), include_concat):
                return True
    ...
```

Next goes our multiplication check. [`divmod`](https://docs.python.org/3/library/functions.html#divmod)
gets both the quotient and remainder of a division; if the remainder is 0, the
division is exact, and thus the target _could_ be the result of a
multiplication.

```py title="2024\day07\solution.py"
def is_solvable(
        numbers: list[int],
        target: int,
        include_concat: bool = False,
) -> bool:
    ...
    # Can the target be the result of a multiplication?
    quotient, remainder = divmod(target, last)
    if remainder == 0:
        if is_solvable(rest, quotient, include_concat):
            return True
    ...
```

And last goes our addition check. We're dealing with only positive integers, so
if the difference between the target and our last number is positive, the target
_could_ be the result of an addition. (And if none of our checks have succeeded,
the target _cannot_ be reached, and the equation is _not_ solvable.)

```py title="2024\day07\solution.py"
def is_solvable(
        numbers: list[int],
        target: int,
        include_concat: bool = False,
) -> bool:
    ...
    # Can the target be the result of an addition?
    difference = target - last
    if difference > 0:
        if is_solvable(rest, difference, include_concat):
            return True

    # If we're here, the answer is no
    return False
```

With this approach, we recurse only if the final operation done on the final
number could possibly result in the target number, which means we skip a lot of
sequences of operators where this is impossible. This speeds up our solution
massively, to about 9 milliseconds on my machine -- way faster than even our
initial Part 1 solution! Take _that_, elephants.
