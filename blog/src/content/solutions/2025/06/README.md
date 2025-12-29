---
year: 2025
day: 6
title: "Trash Compactor"
slug: 2025/day/6
pub_date: "2025-12-06"
# concepts: []
---
## Part 1

Looks like we're doing... cephalopod math? Seems exotic. I think our first step
should be to convert these math problems to a different, more familiar format.

Once we have a list of the rows of our input, we can use
[extended iterable unpacking](https://peps.python.org/pep-3132) to separate the
rows into the top number rows and the bottom symbol row.

```py title="2025\day06\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        *raw_numbers, raw_symbols = self.input
        ...
```

Each row can be split by whitespace with `str.split`, and the numeric rows can
be converted to numbers by mapping the `int` function onto them.

```py title="2025\day06\solution.py" "list(zip(*rows))"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        symbols = raw_symbols.split()
        rows = [map(int, row.split()) for row in raw_numbers]
        number_groups: list[tuple[int, ...]] = list(zip(*rows))
        ...
```

Now, each problem's numbers are grouped in columns instead of rows, so we can't
just use the rows as-is. So in the code above, I instead use a neat trick I
explained on [2023 Day 13](/solutions/2023/day/13): if you have a list of
`rows`, you can iterate through the columns with `zip(*rows)`. Here's what the
result looks like, using the numbers from the sample data:

```py
>>> rows = [
...     [123, 328, 51, 64],
...     [45, 64, 387, 23],
...     [6, 98, 215, 314],
... ]
>>> list(zip(*rows))
[(123, 45, 6),
 (328, 64, 98),
 (51, 387, 215),
 (64, 23, 314)]
```

Now we have two parallel lists: the list of the groups of numbers involved in
each problem, and the list of math symbols used in each problem. This is most of
what we need to get each answer.

We can use `zip()` to iterate through the number groups and symbols for each
math problem. The only thing left to do is write some code that calculates the
answer to each problem, and then adds each answer to a grand total.

```py title="2025\day06\solution.py" /(...)  # TODO/
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        total = 0
        for numbers, symbol in zip(number_groups, symbols):
            ...  # TODO Add solve-math-problem code
        return total
```

For the answer calculations, we can use a concept from [functional programming](https://en.wikipedia.org/wiki/Functional_programming)
called ["folding"](https://en.wikipedia.org/wiki/Fold_(higher-order_function)).
Python includes a function called [`reduce`](https://docs.python.org/dev/library/functools.html#functools.reduce)
in its `functools` module,[^guido-hated-reduce] and it basically does what we
want: it takes an iterable, applies a function to its items from left to right,
and returns a single value as a result.

[^guido-hated-reduce]: Back when Python 2 was current, `reduce()` was a builtin
function. But Python creator Guido van Rossum never really liked the
functional-programming features of Python like `lambda`, `filter()`, and
`map()`; in particular, `reduce()` was the functional-style Python builtin that
he ["always hated most"](https://www.artima.com/weblogs/viewpost.jsp?thread=98196),
and he considered removing it in Python 3 before it was relegated to the
`functools` module.

Combined with various functions from the [operator](https://docs.python.org/3/library/operator.html)
module, this can be used to get the sum or product of a series of numbers, based
on which operator function we pass to it.[^sum-and-math-prod]

[^sum-and-math-prod]: Technically, we could have just used `sum` for addition
and `math.prod` for multiplication, and chosen between the two functions based
on the math symbol. But relying on pre-existing functions that happen to fit our
use case feels too much like a [special case](https://pep20.org/#special) to me.

```py
>>> from functools import reduce
>>> from operator import add, mul
>>> # (123 * 45) * 6 = 33210
>>> reduce(mul, [123, 45, 6])
33210
>>> # (328 + 64) + 98 = 490
>>> reduce(add, [328, 64, 98])
490
>>> # (51 * 387) * 215 = 4243455
>>> reduce(mul, [51, 387, 215])
4243455
>>> # (64 + 23) + 314 = 401
>>> reduce(add, [64, 23, 314])
401
```

So in our calculation loop, we can use `reduce` with the correct operators to
get our answers, and then add them to our grand total.

```py title="2025\day06\solution.py" ins={1-3, 5-8, 16-17}
from collections.abc import Callable
from functools import reduce
from operator import add, mul

OPERATORS: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "*": mul,
}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        total = 0
        for numbers, symbol in zip(number_groups, symbols):
            op = OPERATORS[symbol]
            total += reduce(op, numbers)
        return total
```

:::note
Our calculation loop ended up being simple enough that we can easily transform
it into a one-liner with `sum`.

```py title="2025\day06\solution.py" ins={6-9}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        return sum(
            reduce(OPERATORS[symbol], numbers)
            for numbers, symbol in zip(number_groups, symbols)
        )
```

It does get slightly more [dense](https://pep20.org/#sparse) than I would like,
but in this case, I think it's still fairly understandable at a glance.
:::

This kind of cephalopod math is manageable enough. Let's hope the same will go
for Part 2...

## Part 2

I did expect Part 2's cephalopod math to be harder. What I _didn't_ expect is
the exact _way_ it got harder.

We have to do some extra work to parse the number groups this time, but the
general approach is exactly the same. So before we alter the parsing for Part 2,
let's factor out our calculation loop.

```py title="2025\day06\solution.py" ins=", Iterable, Sequence" ins={5-13,20,27} /(\\(\\))  # TODO/
from collections.abc import Callable, Iterable, Sequence
...

class Solution(StrSplitSolution):
    def _solve(
            self,
            number_groups: Sequence[Iterable[int]],
            symbols: Sequence[str],
    ) -> int:
        return sum(
            reduce(OPERATORS[symbol], numbers)
            for numbers, symbol in zip(number_groups, symbols)
        )

    def part_1(self) -> int:
        *raw_numbers, raw_symbols = self.input

        ...  # Part 1 parsing here

        return self._solve(number_groups, symbols)

    def part_2(self) -> int:
        *raw_numbers, raw_symbols = self.input

        ...  # Part 2 parsing here

        return self._solve(number_groups, symbols)
```

Now let's get to the hard part: parsing the data.

Because the problems are to be read from right to left,[^direction-doesnt-matter]
the symbols can be split up in the same way as before, but reversed with the
`seq[::-1]` idiom for reversing sequences. We'll be doing the same to the
columns, which we can get with the same `zip(*rows)` trick as before.

[^direction-doesnt-matter]: Because we're using addition and multiplication,
which are commutative (i.e. changing the order won't change the result), the
direction we read them in doesn't actually matter. But I chose to read them
backwards to be consistent with the puzzle prompt.

```py title="2025\day06\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        symbols = raw_symbols.split()[::-1]
        columns = list(zip(*raw_numbers))[::-1]
        ...
```

But how do we turn the columns into number groups? Each group of numbers in the
input is separated by a column of all spaces, so the first thing we'll want to
do is (in effect) split the columns into groups using the all-spaces columns as
separators.

This part actually took me a while to figure out how to do effectively. At
first, I went with a pretty complicated approach involving [`itertools.pairwise`](https://docs.python.org/3/library/itertools.html#itertools.pairwise)
with pairs of string indices. But as I was Googling for a better approach, I
found that this group-splitting thing could be done using the [`itertools.groupby`](https://docs.python.org/3/library/itertools.html#itertools.groupby)
function[^groups] -- which is exciting, because it's a neat function I rarely
ever use.

[^groups]: This is secretly why I've been calling them "groups" throughout this
writeup. Hindsight really _is_ 20/20, isn't it?

`itertools.groupby` lets you divide an iterable into groups using a key
function, and consecutive items with the same key will be grouped together. The
result is an iterator of `(key, group)` pairs, where `key` is the value used for
making the group, and `group` is the group itself as an iterator.

```py
>>> from itertools import groupby
>>> data = "abc.de..f...ghi"
>>> is_dot = lambda ch: ch == "."
>>> [(key, list(group)) for key, group in groupby(data, key=is_dot)]
[(False, ['a', 'b', 'c']),
 (True, ['.']),
 (False, ['d', 'e']),
 (True, ['.', '.']),
 (False, ['f']),
 (True, ['.', '.', '.']),
 (False, ['g', 'h', 'i'])]
```

In the above example, our key function checks whether a character is a dot, and
so the `key` of each group is `True` if the group is made up of dots, and
`False` if it isn't. All of the consecutive dots and non-dots are then grouped
together like we expect.

We can use this same technique to do our group-splitting; our key function will
check whether all items in the column are spaces, and we can simply keep the
column groups where that key is false. And once we have each column group, we
can do `int("".join(column))` on each of its columns to turn them into numbers
like we want.

```py title="2025\day06\solution.py" ins={1,9-10,14-18}
from itertools import groupby
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        def is_all_spaces(column: Sequence[str]) -> bool:
            return all(char == " " for char in column)

        symbols = raw_symbols.split()[::-1]
        columns = list(zip(*raw_numbers))[::-1]
        number_groups = [
            [int("".join(column)) for column in group]
            for is_separator, group in groupby(columns, key=is_all_spaces)
            if not is_separator
        ]
        ...
```

From here, the solution is exactly the same as before.

It's neat that we got to use `itertools.groupby` today; I like discovering
hidden gems in the standard library like that.
