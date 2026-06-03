---
year: 2024
day: 13
title: "Claw Contraption"
slug: 2024/day/13
pub_date: "2026-06-03"
# concepts: []
---
## Part 1

I've never been good at those claw machines. But something tells me I'll do okay
at this one.

Each claw machine can be modeled as a series of [linear equations](https://en.wikipedia.org/wiki/Linear_equation)
-- which the original prompt even shows you how to do for the first claw machine
in the sample input:

```text
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400
```

The solution to this claw machine is to press A 80 times and press B 40 times,
because:

- `80*94 + 40*22 = 8400` -- i.e. the claw's X equals the prize's X.
- `80*34 + 40*67 = 5400` -- i.e. the claw's Y equals the prize's Y.

Let's write a more general form of these equations. Let's call the number of A
and B presses $A$ and $B$, the X/Y effect of A and B presses $(x_A, y_A)$ and
$(x_B, y_B)$ respectively, and the X/Y position of the prize $(x_p, y_p)$; with
these variables, the linear equations will look something like this, and we'll
want to solve them for $A$ and $B$.

$$
\begin{align*}
A \cdot x_A + B \cdot x_B &= x_p \\
A \cdot y_A + B \cdot y_B &= y_p
\end{align*}
$$

I had to deal with similar-looking linear equations during [2023 Day 24](/solutions/2023/day/24),
and they're not too tricky to solve using algebra. But because we're computer
scientists and not mathematicians today, we can use the external Python library
[Sympy](https://www.sympy.org/) to make quick work of the algebra.

First, we define all our variables using SymPy's `symbols` function.

```py
>>> from sympy import *
>>> init_printing(use_unicode=False)
>>> ax, ay, bx, by = symbols("ax ay bx by")
>>> px, py = symbols("px py")
>>> A, B = symbols("A B")
```

Second, we create an equation (which SymPy calls an `Eq`) for the X and Y
positions.

```py
>>> # The claw's X/Y should equal the prize's X/Y
>>> eqx = Eq(A * ax + B * bx, px)
>>> eqy = Eq(A * ay + B * by, py)
```

And lastly, we use Sympy's `solve` function to solve those equations for `A` and
`B`.

```py
>>> solve([eqx, eqy], A, B)
    -bx*py + by*px     ax*py - ay*px
{A: --------------, B: -------------}
    ax*by - ay*bx      ax*by - ay*bx
```

$$
\begin{align*}
A &= \frac{- x_B \cdot y_p + y_B \cdot x_p}{x_A \cdot y_B - y_A \cdot x_B} \\
B &= \frac{x_A \cdot y_p - y_A \cdot x_p}{x_A \cdot y_B - y_A \cdot x_B}
\end{align*}
$$

We'll be using these solutions in our code. Because they are both in the form of
fractions, it makes sense to use the builtin [`fractions`](https://docs.python.org/3/library/fractions.html)
module to represent them as `Fraction`s; they even have the same denominator,
which will make our code to calculate them slightly simpler.[^denominator-0]

[^denominator-0]: If you're like most math-conscious people, you may be a little
worried about what will happen if the denominator is 0; after all, you famously
can't divide by 0 -- that is, unless you're willing to accept [the consequences](https://youtu.be/eR23nPNqf6A).

    - In terms of our puzzle, it would mean that the claw machine we're looking
    at has _no_ solutions, and we should ignore it.
    - In terms of our _code_, the `Fraction` constructor will raise a
    `ZeroDivisionError`, and our program would stop.

    I don't give this case any special handling because it turns out to never
    happen -- and it's generally better _not_ to silence potentially important
    [errors](https://pep20.org/#errors).

```py title="2024\day13\solution.py"
from fractions import Fraction

def solve_machine(
        ax: int, ay: int, bx: int, by: int, prize_x: int, prize_y: int,
) -> tuple[Fraction, Fraction]:
    # NOTE The X/Y position of the claw after the A and B presses can be
    # modeled as linear equations. We can solve these equations for the
    # number of A and B presses using some algebra.
    denominator = ax * by - ay * bx
    a_presses = Fraction(-bx * prize_y + by * prize_x, denominator)
    b_presses = Fraction( ax * prize_y - ay * prize_x, denominator)
    return a_presses, b_presses
```

Now we can focus on input parsing. Each claw machine "block" from the input is
separated by two newlines (my AoC solution framework has a feature to split them
automatically, but you may need to do that manually with [`str.split`](https://docs.python.org/3/library/stdtypes.html#str.split)).
And while parsing each block might normally be a pain, in this case we can use
the `re` module to simply extract everything that looks like a number and
convert them to `int`s.[^argument-order]

[^argument-order]: This is why I implemented `solve_machine` to take its
arguments in the same order they appear in the input; I can call it on a list
`machine` using the syntax `solve_machine(*machine)`. The [simpler](https://pep20.org/#simple)
I can make that part of the code, the better.

``` py
>>> import re
>>> block = """Button A: X+94, Y+34
... Button B: X+22, Y+67
... Prize: X=8400, Y=5400"""
>>> [int(m) for m in re.findall(r"\d+", block)]
[94, 34, 22, 67, 8400, 5400]
```

Our solution from here is extremely easy. The one subtlety to keep in mind is
that we only want to count solutions with exact integer numbers of A and B
presses[^negative-presses] -- no [half A presses](https://youtu.be/kpk2tdsPh0A)
here! -- which we can check using the [`is_integer`](https://docs.python.org/3/library/fractions.html#fractions.Fraction.is_integer)
method of `Fraction`s.

[^negative-presses]: Technically, we'd also want to verify that we don't have a
_negative_ number of presses either... but this never happens, because the prize
is never at a negative X or Y position. (Good thing, too, or else that would
make these claw machines _super_ unfair!)

```py title="2024\day13\solution.py"
import re
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        total = 0
        for block in self.input:
            machine = [int(m) for m in re.findall(r"\d+", block)]

            a, b = solve_machine(*machine)
            # "An A press is an A press; you can't say it's only a half"
            if a.is_integer() and b.is_integer():
                total += 3 * a + b

        return int(total)
```

Pure number crunching, exactly what the computer is built to do. I love to see
it.

## Part 2

Bigger numbers? Farther-out prizes? You don't scare me, arcade!

The only thing that changes here is that we have to add 10 trillion to the claw
machine's prize X/Y values; it doesn't take much to factor out the main solution
and make that change for Part 2.

```py title="2024\day13\solution.py" ins=/def (_solve)/ ins=", prize_offset: int = 0" ins={10-12,21-25}
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def _solve(self, prize_offset: int = 0) -> int:
        total = 0
        for block in self.input:
            machine = [int(m) for m in re.findall(r"\d+", block)]
            # Add offset to prize position
            machine[4] += prize_offset
            machine[5] += prize_offset

            a, b = solve_machine(*machine)
            # "An A press is an A press; you can't say it's only a half"
            if a.is_integer() and b.is_integer():
                total += 3 * a + b

        return int(total)

    def part_1(self) -> int:
        return self._solve()

    def part_2(self) -> int:
        return self._solve(prize_offset=10_000_000_000_000)
```

And because the underlying machine-solving function uses only a few simple
mathematical operations, we see almost _no_ speed penalty for the increased
prize distance. Those prizes are _ours_!
