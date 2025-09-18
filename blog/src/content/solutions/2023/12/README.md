---
year: 2023
day: 12
title: "Hot Springs"
slug: 2023/day/12
pub_date: "2025-10-22"
# concepts: [recursion]
---
## Part 1

It's [Picross](https://en.wikipedia.org/wiki/Nonogram)! Only we're not solving a
Picross puzzle, but counting solutions for single rows. We could brute-force
every possible solution (and I did at first!), but let's instead do something a
bit more clever.

First, the easy part: if we have a function for counting the number of
solutions for a row, we can simply apply it to each row and `sum` the results.

```py title="2023\day12\solution.py" "num_solutions"
def solve_line(line: str) -> int:
    record, raw_shape = line.split()
    groups = tuple(map(int, raw_shape.split(",")))
    return num_solutions(record, groups)

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(solve_line(line) for line in self.input)
```

Now to implement `num_solutions`. We can think about this recursively, though we
need to be careful; there are actually _two_ base cases to consider, depending
on how many groups of `#`s we have yet to look at.

- **Base case(s)**
    - If there are no groups we need to match, then the answer depends on
    whether any `#` characters are left in the record. If there aren't, then
    _one solution_ is possible -- the one where every `?` is treated as a `.`.
    If there are, then there's no other group for any `#` to correspond to, and
    _no solutions_ are possible.
    - If there are still some groups left to match, then the answer depends on
    the size of the record. If we know that the size of the groups can't
    possibly fit into the size of the record, then _no solutions_ are possible;
    otherwise, we don't have enough information yet to return an answer.

We can implement these base cases pretty easily. `not groups` will be true if
`groups` is empty. Similarly, a lazy way to check whether the groups will fit in
the record is by checking whether the record is empty (i.e. `not record`) --
after all, the groups won't fit if there's literally _no_ space for them, right?

```py title="2023\day12\solution.py"
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    # If there are no groups
    if not groups:
        # No solutions if there are unaccounted-for `#`s in the record;
        # one solution if there aren't (where every `?` is a `.`)
        return 0 if "#" in record else 1
    # There are groups; no solutions if they can't possibly fit in the
    # rest of the record
    if not record:
        return 0
    ...
```

:::note
There's an interesting optimization we can make when checking whether the groups
can possibly fit in the record.

If we consider how much space a collection of groups will take up, they'll need
as many `#`s as each group requires, plus a `.` between each pair of groups.

```py "sum(groups) + len(groups) - 1 > len(record)"
if sum(groups) + len(groups) - 1 > len(record):
    return 0
```

Changing the condition to reflect this will speed up the function, because it's
not doing some recursive cases it otherwise would have.
:::

There are also _three_ recursive cases to consider, depending on which character
the record starts with. We'll be consuming `record` and `groups` from left to
right until one of the base cases is reached.

If we come across a `.`, we can simply ignore it.

```py title="2023\day12\solution.py"
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
    char, rest = record[0], record[1:]
    if char == ".":
        # Find solutions going through rest of records
        return num_solutions(rest, groups)
    ...
```

If we come across a `#`, then we're at the first character of a group. First, we
must verify that this group has the exact number of `#`s required (where we're
treating every `?` in this group as a `#`). If so, we remove that group from the
`records` and `groups` and we recurse; if not, there are _no solutions_.

```py title="2023\day12\solution.py"
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
    elif char == "#":
        group = groups[0]
        # No solutions if the record isn't long enough for this group
        if len(record) < group:
            return 0
        # No solutions if any `.`s are in this group
        if "." in record[:group]:
            return 0
        # No solutions if a `#` is just after this group (which would
        # make the group bigger)
        if len(record) > group and record[group] == "#":
            return 0
        # Find solutions after removing this group
        return num_solutions(record[group + 1 :], groups[1:])
    ...
```

Finally, if we come across a `?`, then we count the solutions we'd get if it was
a `.`, count the solutions we'd get if it was a `#`, and add them together.

```py title="2023\day12\solution.py"
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
    else:
        # Find solutions after substituting either character
        return (
            num_solutions("#" + rest, groups)
            + num_solutions("." + rest, groups)
        )
```

We now have our base cases and recursive cases, which will work for tallying up
the number of solutions for any Picross row.

## Part 2

Preparing our `solve_line` function to run Part 2 isn't too hard. (It's made
easier by the fact that we can literally multiply sequences to repeat them!)

```py title="2023\day12\solution.py" ins=", with_multiplier: bool = False" ins={4-6,13-17}
def solve_line(line: str, with_multiplier: bool = False) -> int:
    record, raw_shape = line.split()
    groups = tuple(map(int, raw_shape.split(",")))
    if with_multiplier:
        record = "?".join([record] * 5)
        groups *= 5
    return num_solutions(record, groups)

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(solve_line(line) for line in self.input)

    def part_2(self) -> int:
        return sum(
            solve_line(line, with_multiplier=True)
            for line in self.input
        )
```

But this will _not_ spit out an answer in a timely manner. It's not hard to see
why; we're basically adding 1 to our answer whenever we get to a valid base
case, and the final answer's going to involve a _massive_ amount of these +1s.
So maybe we can save ourselves a bit of that work?

As it turns out, we can, using [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache)!
It is a useful example of a [decorator](https://docs.python.org/3/glossary.html#term-decorator)
-- something which can transform a function to modify its behavior. The way
`functools.cache` modifies a function is by _caching_ its outputs, so that
repeated calculations can reuse the previously calculated answers.

```py
>>> # Fibonacci function
>>> fib = lambda n: n if n<2 else fib(n-2)+fib(n-1)
>>> 
>>> from timeit import timeit
>>> # Time to get fib(45) without cache
>>> timeit(lambda: fib(45), number=1)
105.6747285000747
>>> # Time to get fib(45) with cache
>>> from functools import cache
>>> fib = cache(fib)
>>> timeit(lambda: fib(45), number=1)
0.00012179999612271786
```

As you can see in the example above, it takes ~100 seconds to get the 45th
Fibonacci number without caching, but _~0.1 milliseconds_ to get it _with_
caching! That's the power of being able to reuse computations.

Adding the `@cache` decorator to `num_solutions` will do the trick,[^hashable-args]
and get our solution running in well under a second.

[^hashable-args]: One thing to remember about `functools.cache` is that the
arguments of whatever function you're decorating need to be [hashable](https://docs.python.org/3/glossary.html#term-hashable).
This is because a `dict` is used to cache the function results, and the keys of
a `dict` must be hashable.

    For example, the `groups` argument cannot be a list of ints, because lists
    are not hashable; it can, however, be a _tuple_ of ints, because tuples of
    ints _are_ hashable.

```py title="2023\day12\solution.py" ins={1,3}
from functools import cache

@cache
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
```

:::note
Adding `@cache` above the function definition is the same as doing the
following:

```py {5}
from functools import cache

def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
num_solutions = cache(num_solutions)
```

The `@` syntax is simply syntactic sugar.
:::
