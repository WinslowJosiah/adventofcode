---
year: 2023
day: 24
title: "Never Tell Me The Odds"
slug: 2023/day/24
pub_date: "2025-11-23"
# concepts: []
---
## Part 1

This puzzle seems way more algebra-heavy than usual. So much so, in fact, that
many Python solutions use external libraries to do the algebra for them. I'll
avoid using any external libraries in my solution directly -- but I _will_ make
use of one to help me with some of the algebra.

We will first create a simple `Hailstone` class with X/Y/Z positions and X/Y/Z
velocities, and give it a `parse` method that parses a line of input into a
`Hailstone`. We've done something like this many times this year.

```py title="2023\day24\solution.py"
from dataclasses import dataclass

def parse_3d_point(point: str) -> list[int]:
    return list(map(int, point.split(", ")))

@dataclass(frozen=True)
class Hailstone:
    px: int
    py: int
    pz: int
    vx: int
    vy: int
    vz: int

    @classmethod
    def parse(cls, line: str) -> Hailstone:
        position, velocity = line.split(" @ ")
        return Hailstone(*parse_3d_point(position), *parse_3d_point(velocity))
    ...
```

We can then use this function to gather the hailstones into a list. Again,
nothing we haven't done before.

```py title="2023\day24\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]
        ...
```

The interesting part is figuring out which hailstones will cross paths with each
other. Sounds like the kind of thing we could put into a function; let's write
the signature of such a function now, and worry about implementing it later.

```py title="2023\day24\solution.py"
from fractions import Fraction

@dataclass(frozen=True)
class Hailstone:
    ...
    def intersection_with(self,
            other: Hailstone,
    ) -> tuple[Fraction, Fraction] | None:
        ...  # TODO Add find-intersection-point code
```

This function will find the point at which a hailstone crosses the path of
another given hailstone. All we know at this point is that we want it to return
an intersection point if it exists, and `None` if it doesn't. (I'm choosing to
make each coordinate a [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html),
because I at least know it will be a rational number.)

:::tip
There are a few ways to represent decimal numbers in Python: as a `float`, as a
[`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal).
and as a [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html).
Each have their own strengths and weaknesses:

- A `float` is are stored as a [floating-point number](https://en.wikipedia.org/wiki/Floating-point_arithmetic)
-- specifically ["double-precision"](https://en.wikipedia.org/wiki/Double-precision_floating-point_format)
-- and calculations with them can be done very fast. However, floating-point
numbers have a limited precision, which can make [some calculations](https://0.30000000000000004.com)
slightly inaccurate. (Though unless you have a specific reason to use `Decimal`
or `Fraction` instead, this is fine.)
- A `decimal.Decimal` is stored as a series of decimal digits with some
precision - 28 places by default - and arithmetic on `Decimal` objects works
basically like you'd expect. However, they are much slower to use than `float`s.
- A `fractions.Fraction` is stored as a numerator and denominator, and
arithmetic on `Fraction` objects is arbitrary-precision and exact. However, they
can only correctly represent exact rational numbers.

:::

From here, it's only a matter of running this intersection function on every
pair of hailstones -- which we can do with [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
-- and adding to a total if the intersection point is within the bounds of the
test area.

```py title="2023\day24\solution.py"
from itertools import combinations
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        BOUNDS_MIN, BOUNDS_MAX = 200_000_000_000_000, 400_000_000_000_000

        total = 0
        for l, r in combinations(hailstones, 2):
            intersection = l.intersection_with(r)
            if intersection is None:
                continue

            x_intersection, y_intersection = intersection
            if (
                BOUNDS_MIN <= x_intersection <= BOUNDS_MAX
                and BOUNDS_MIN <= y_intersection <= BOUNDS_MAX
            ):
                total += 1

        return total
```

Now to do the interesting part: finding the intersection point of two
hailstones. Time for some algebra!

---

Let's call hailstone $n$'s starting X and Y position $x_n$ and $y_n$, and let's
call its X and Y velocity $u_n$ and $v_n$. Their X and Y positions at time $t$
can be modeled with the following functions:

$$
\begin{align*}
X_n(t) &= x_n + t u_n \\
Y_n(t) &= y_n + t v_n
\end{align*}
$$

For completeness, we can call its starting Z position $z_n$, and its Z velocity
$w_n$. Then its Z position at time $t$ can be modeled with the following
function (but we don't need it yet):

$$
Z_n(t) = z_n + t w_n
$$

Let's consider two hailstones, hailstone 1 and hailstone 2. We want to know if
their paths ever cross -- i.e. if their X and Y positions are ever equal -- and
we want to know at what times $t_1$ and $t_2$ they reach that position. We can
model that with a system of equations, which we'll want to solve for $t_1$ and
$t_2$.

$$
\begin{align*}
X_1(t_1) &= X_2(t_2) \\
Y_1(t_1) &= Y_2(t_2)
\end{align*}
$$

In terms of $x_n$, $y_n$, and the other variables, the equations look like this:

$$
\begin{align*}
x_1 + t_1 u_1 &= x_2 + t_2 u_2 \\
y_1 + t_1 v_1 &= y_2 + t_2 v_2
\end{align*}
$$

That... looks hard to solve. I know there's a trick to it,[^solve-for-t1-and-t2]
but instead, let's give it to the external library [SymPy](https://www.sympy.org)
and see what it can do!

[^solve-for-t1-and-t2]: The trick is to get the $t_1$ and $t_2$ terms to one
side...

    $$
    \begin{align*}
    t_1 u_1 - t_2 u_2 &= x_2 - x_1 \\
    t_1 v_1 - t_2 v_2 &= y_2 - y_1
    \end{align*}
    $$

    ...multiply each equation with something such that the $t_2$ term is the
    same in both...

    $$
    \begin{align*}
    v_2 (t_1 u_1 - t_2 u_2) &= v_2 (x_2 - x_1) \\
    u_2 (t_1 v_1 - t_2 v_2) &= u_2 (y_2 - y_1) \\
    \\
    t_1 u_1 v_2 - t_2 u_2 v_2 &= v_2 (x_2 - x_1) \\
    t_1 u_2 v_1 - t_2 u_2 v_2 &= u_2 (y_2 - y_1)
    \end{align*}
    $$

    ...then subtract one equation from the other.

    $$
    \begin{alignedat}{2}
                  t_1 u_1 v_2 &- t_2 u_2 v_2 &&= v_2 (x_2 - x_1) \\
    -\phantom{-}  t_1 u_2 v_1 &- t_2 u_2 v_2 &&= u_2 (y_2 - y_1) \\
    \hline
    t_1 u_1 v_2 - t_1 u_2 v_1 &              &&= v_2 (x_2 - x_1) - u_2 (y_2 - y_1)
    \end{alignedat}
    $$

    Now we have an equation in terms of $t_1$, which can be solved fairly
    easily. A similar thing can be done to isolate $t_2$ and solve for it as
    well.

    I could've done all of that algebra in the main text, but in my opinion,
    doing it with SymPy instead makes the process less error-prone. (Plus, I
    think SymPy is pretty cool, and I wanted an excuse to use it.)

Very basically, SymPy allows us to manipulate mathematical expressions with
"symbols", which we can create using the `symbols` function.

```py
>>> from sympy import *
>>> init_printing(use_unicode=False)
>>> t1, t2 = symbols("t1 t2")
>>> u1, v1, x1, y1 = symbols("u1 v1 x1 y1")
>>> u2, v2, x2, y2 = symbols("u2 v2 x2 y2")
```

We want to solve a system of two equations, which we can create with `Eq`. Here,
`eqx` will be our X position equation, and `eqy` will be our Y position
equation.

```py
>>> # The X positions should be equal
>>> eqx = Eq(x1 + t1 * u1, x2 + t2 * u2)
>>> # The Y positions should be equal
>>> eqy = Eq(y1 + t1 * v1, y2 + t2 * v2)
```

Equations can be solved by passing them to `solve`. Here, we want to solve the
equations `eqx` and `eqy` for the variables `t1` and `t2`; doing that gives us
the following result:

```py
>>> solve([eqx, eqy], t1, t2)

     u2*y1 - u2*y2 - v2*x1 + v2*x2      u1*y1 - u1*y2 - v1*x1 + v1*x2
{t1: -----------------------------, t2: -----------------------------}
             u1*v2 - u2*v1                      u1*v2 - u2*v1
```

We now have solutions for $t_1$ and $t_2$! I'll rewrite them below (and pull out
some common factors in the numerators):

$$
\begin{align*}
t_1 &= \frac{u_2 (y_1 - y_2) - v_2 (x_1 - x_2)}{u_1 v_2 - u_2 v_1} \\
t_2 &= \frac{u_1 (y_1 - y_2) - v_1 (x_1 - x_2)}{u_1 v_2 - u_2 v_1}
\end{align*}
$$

Notice that they have the same denominator ($u_1 v_2 - u_2 v_1$) -- which is
awfully convenient, because we can avoid computing it twice. Also notice that,
if the denominator is 0, then the values of $t_1$ and $t_2$ are undefined[^equal-slopes]
-- which allows for an easy condition to check whether an intersection point
exists.

[^equal-slopes]: Which only happens if $u_1 / u_2 = v_1 / v_2$ -- i.e. if the
slopes are equal. This makes sense; in this case, either the lines are parallel
and never intersect, or the lines are coincident and _always_ intersect -- so it
doesn't make sense to return any single intersection point.

We can directly use these solutions in our `intersection_with` function. We will
return `None` if the denominator of the fraction is 0; otherwise, we will
calculate the crossing time, and then use that crossing time to find where the
hailstone will be when it crosses the other hailstone's path.

```py title="2023\day24\solution.py" ins={7-24}
@dataclass(frozen=True)
class Hailstone:
    ...
    def intersection_with(self,
            other: Hailstone,
    ) -> tuple[Fraction, Fraction] | None:
        denominator = other.vx * self.vy - other.vy * self.vx
        # If this denominator is 0, the lines are parallel or coincident
        if denominator == 0:
            return None

        # When does this hailstone intersect the other one?
        self_t = Fraction(
            other.vx * (other.py - self.py) - other.vy * (other.px - self.px),
            denominator,
        )
        # When does the other hailstone intersect this one?
        other_t = Fraction(
            self.vx * (other.py - self.py) - self.vy * (other.px - self.px),
            denominator,
        )

        # Get the position of this hailstone when it intersects
        return self.px + self_t * self.vx, self.py + self_t * self.vy
```

Sadly, we're not _quite_ done yet, because we forgot one thing: we don't want to
count intersections that happened in the past. Let's add a special parameter
when we call the function...

```py title="2023\day24\solution.py" ins=", future_only=True"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        for l, r in combinations(hailstones, 2):
            intersection = l.intersection_with(r, future_only=True)
            if intersection is None:
                continue
            ...
        ...
```

...and if that special parameter is true, make the function return `None` for
intersections that happened at past time values.

```py title="2023\day24\solution.py" ins={6-7,10-11}
@dataclass(frozen=True)
class Hailstone:
    ...
    def intersection_with(self,
            other: Hailstone,
            *,
            future_only: bool = False,
    ) -> tuple[Fraction, Fraction] | None:
        ...
        if future_only and (self_t < 0 or other_t < 0):
            return None

        # Get the position of this hailstone when it intersects
        return self.px + self_t * self.vx, self.py + self_t * self.vy
```

Phew, we made it out alive with a solution to Part 1! But I'm worried about what
we'll have to do with the Z values in Part 2...

## Part 2

I was afraid this would happen.

Solving algebraically for the position and velocity of the rock would be
_extremely_ difficult without using something like SymPy. In fact,
[my original solution](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2023/day24/__init__.py#L61-L118)
ended up using SymPy to solve a large system of equations.

But I wanted a more clever solution that _doesn't_ use any external libraries,
and also doesn't require us to build an entire [computer algebra system](https://en.wikipedia.org/wiki/Computer_algebra_system)
from scratch. I looked through [the Reddit solution thread](https://reddit.com/comments/18pnycy)
and found [this solution by `u/TheZigerionScammer`](https://reddit.com/comments/18pnycy/comment/keqf8uq)
that _definitely_ has a clever insight. What did they see that took me an entire
algebra-based Python library to see? I've adapted their approach with a few
differences,[^a-few-differences] and I'll take the time to explain it below.

[^a-few-differences]: The main difference to be aware of is how the possible
rock velocities are found. `u/TheZigerionScammer` brute-forces values from
-1,000 to 1,000, checking whether they are solutions to some modular equation; I
describe exactly what those solutions _look_ like, so I can calculate them
(mostly) directly.

    My approach is slower, but it's more robust; after all, what if (say) the
    rock's Y velocity is 1,821... uh, units... per nanosecond? (Wow, I _just_
    realized that the prompt doesn't even say what the units for `px` and `vx`
    are.)

### Velocity

Let's consider two hailstones `A` and `B` which both have a `vx` of 0 -- i.e.
they're not moving in the X dimension. However fast we throw the rock, its speed
must be such that it _could_ collide with both hailstones. So if the rock
collides with hailstone `A`, it must cover the distance to hailstone `B` in some
integer amount of time -- and its X position must be an integer at every point.

Let's look at a concrete example, where `A` has a `px` of 2 and `B` has a `px`
of 8. If the rock starts at the position of `A`, here are the possible rock X
velocities that could hit `B`, and the corresponding hit times (note that
negative times mean `B` was hit _in the past_):

| Rock `vx` |     Rock `px` Over Time      | Time Of Hit |
| :-------: | :--------------------------: | :---------: |
|     1     | 2, 3, 4, 5, 6, 7, **8**, ... |      6      |
|     2     |     2, 4, 6, **8**, ...      |      3      |
|     3     |       2, 5, **8**, ...       |      2      |
|     6     |        2, **8**, ...         |      1      |
|    -6     |        ..., **8**, 2         |     -1      |
|    -3     |       ..., **8**, 5, 2       |     -2      |
|    -2     |     ..., **8**, 6, 4, 2      |     -3      |
|    -1     | ..., **8**, 7, 6, 5, 4, 3, 2 |     -6      |

The possible hit times are exactly the positive and negative divisors of 6 (the
distance between `A` and `B`)! And because velocity is distance over time, the
possible `vx` values will _also_ be those divisors.

This line of thinking also extends to hailstones that _share_ a `vx` value (i.e.
parallel hailstones); we would simply need to add that shared hailstone `vx` to
each possible rock `vx`. For example, if `A` and `B` shared a `vx` of 4, here's
how their `px` values would change over time:

| Time | `px` Of `A` | `px` of `B` |
| :--: | :---------: | :---------: |
| ...  |     ...     |     ...     |
|  -6  |     -22     |     -16     |
|  -5  |     -18     |     -12     |
|  -4  |     -14     |     -8      |
|  -3  |     -10     |     -4      |
|  -2  |     -6      |      0      |
|  -1  |     -2      |      4      |
|  0   |      2      |      8      |
|  1   |      6      |     12      |
|  2   |     10      |     16      |
|  3   |     14      |     20      |
|  4   |     18      |     24      |
|  5   |     22      |     28      |
|  6   |     26      |     32      |
| ...  |     ...     |     ...     |

And here's how the possible rock X velocities would change:

|    Rock `vx`    |          Rock `px` Over Time          | Time Of Hit |
| :-------------: | :-----------------------------------: | :---------: |
|  1 + 4 = **5**  |   2, 7, 12, 17, 22, 27, **32** ...    |      6      |
|  2 + 4 = **6**  |         2, 8, 14, **20**, ...         |      3      |
|  3 + 4 = **7**  |           2, 9, **16**, ...           |      2      |
| 6 + 4 = **10**  |            2, **12**, ...             |      1      |
| -6 + 4 = **-2** |             ..., **4**, 2             |     -1      |
| -3 + 4 = **1**  |           ..., **0**, 1, 2            |     -2      |
| -2 + 4 = **2**  |         ..., **-4**, -2, 0, 2         |     -3      |
| -1 + 4 = **3**  | ..., **-16**, -13, -10, -7, -4, -1, 2 |     -6      |

This narrows down the possible rock `vx` values _considerably_. And since the
rock must collide with _all_ hailstones, its only possible `vx` values will be
whatever `vx` values we find for _all_ such pairs of parallel hailstones! (Of
course, the same thinking applies for possible `vy` values and `vz` values.)

Once we've done this process, we could happen to find several `vx`/`vy`/`vz`
triplets that work -- indeed, this process finds 64 such triplets for the sample
input (though only one leads us to a valid `px`/`py`/`pz` triplet). But as it
turns out, if we do this process on the full puzzle input, we happen to find
only _one_ velocity triplet! Therefore, the one we find must be the right one
(if there is a "right one" at all... which there is).

---

Let's convert this clever condition to code.

First, let's write a function to calculate the divisors of a number. For this, I
ended up adapting [this function](https://alexwlchan.net/2019/finding-divisors-with-python)
I found on the internet; it runs decently fast for numbers with many small prime
factors, which is true of the numbers we're working with.

```py title="2023\day24\solution.py" ins=", product"
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, product
from math import prod

def divisors(n: int) -> Iterator[int]:
    # Gather prime factors and their exponents
    prime_factors: Counter[int] = Counter()
    factor = 2
    while factor * factor <= n:
        if n % factor == 0:
            n //= factor
            prime_factors[factor] += 1
        else:
            factor += 1
    if n > 1:
        prime_factors[n] += 1

    # Generate all combinations of prime factors to form divisors
    powers: list[list[int]] = [
        [factor ** i for i in range(count + 1)]
        for factor, count in prime_factors.items()
    ]
    for group in product(*powers):
        yield prod(group)
```

Next, let's use this `divisors` function to calculate the possible rock
velocities for each pair of parallel hailstones -- i.e. the shared hailstone
velocity, plus each positive and negative divisor of the distance between the
hailstones.

```py title="2023\day24\solution.py"
def possible_rock_velocities(
        hailstone_velocity: int,
        distance: int,
) -> set[int]:
    return {
        hailstone_velocity + v
        for rock_velocity in divisors(abs(distance))
        for v in (-rock_velocity, rock_velocity)
    }
```

We can do this for each of the X, Y, and Z dimensions separately -- which will
be made easier by using [`getattr`](https://docs.python.org/3/library/functions.html#getattr)
to write `position` and `velocity` helper functions.

We'll end up with several `set`s of rock velocities that can hit each parallel
pair, and the [`intersection`](https://docs.python.org/3/library/stdtypes.html#frozenset.intersection)
(common items) of all the sets[^intersection-of-sets] are the rock velocities
that can hit _all_ parallel pairs. (As I said before, we can assume that there's
only one such rock velocity.)

[^intersection-of-sets]: Technically, I take the `intersection` of all the sets
_with the first set_ (i.e. `sets[0].intersection(*sets)`); that's about the
simplest way I can express this.

```py title="2023\day24\solution.py"
@dataclass(frozen=True)
class Hailstone:
    ...
    def position(self, dim: str) -> int:
        assert dim in "xyz", f"invalid dimension: {dim}"
        return getattr(self, f"p{dim}")

    def velocity(self, dim: str) -> int:
        assert dim in "xyz", f"invalid dimension: {dim}"
        return getattr(self, f"v{dim}")
    ...

def get_rock_velocity(hailstones: list[Hailstone], dim: str) -> int:
    # For each pair of parallel hailstones, calculate every possible
    # rock velocity that could hit them both
    rock_velocities = [
        possible_rock_velocities(
            hailstone_velocity=l.velocity(dim),
            distance=r.position(dim) - l.position(dim),
        )
        for l, r in combinations(hailstones, 2)
        if l.velocity(dim) == r.velocity(dim)
    ]
    # Return the (assumed unique) velocity that could hit every pair of
    # parallel hailstones
    shared_rock_velocities = rock_velocities[0].intersection(*rock_velocities)
    assert len(shared_rock_velocities) == 1, f"unique {dim} velocity not found"
    return shared_rock_velocities.pop()
```

Doing this process for each of the X, Y, and Z dimensions finally gives us the
velocity of the rock! (_Phew_.)

```py title="2023\day24\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]
        rvx, rvy, rvz = (get_rock_velocity(hailstones, dim) for dim in "xyz")
        ...
```

### Position

We now know the exact velocity of the rock. Using this, we can perform a neat
trick for getting the starting position of the rock.

Let's imagine what the paths of the hailstones would look like relative to the
rock -- i.e. in a reference frame where the rock is sitting still. The rock has
to collide with every single hailstone, so in this reference frame, the paths of
all the hailstones would intersect at a single point: the (stationary) position
of the rock.

We can already start implementing this idea into code. First, let's add a helper
function to create a version of a hailstone with the X and Y velocities changed,
so that they're relative to the rock's X and Y velocity.

```py title="2023\day24\solution.py"
@dataclass(frozen=True)
class Hailstone:
    ...
    def relative_to_rock_velocity(self, rvx: int, rvy: int) -> Hailstone:
        return Hailstone(
            self.px, self.py, self.pz,
            self.vx - rvx, self.vy - rvy, self.vz,
        )
```

Luckily for us, we already have a function to get the intersection point of two
hailstones' paths, which will give us the X and Y position of that intersection
point. So next, let's use that function to get the intersection point of two
"relative hailstones"; it doesn't matter which two they are, as long as a unique
intersection point is found.

```py title="2023\day24\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        # Find the X/Y position of the rock for it to hit two hailstones
        # NOTE We check all pairs here, since some pairs of hailstones
        # may be collinear relative to the rock (and thus fail to find a
        # unique intersection point).
        intersection = None
        for a, b in combinations(hailstones, 2):
            a_relative = a.relative_to_rock_velocity(rvx, rvy)
            b_relative = b.relative_to_rock_velocity(rvx, rvy)
            intersection = a_relative.intersection_with(b_relative)
            if intersection is not None:
                break
        else:
            raise ValueError("could not find starting X/Y for rock")

        rpx, rpy = intersection
        assert rpx.is_integer(), "rock's x position is not an integer"
        assert rpy.is_integer(), "rock's y position is not an integer"
        ...
```

:::note
As a sanity check, I check whether the intersection point is an integer; I use
the [`is_integer`](https://docs.python.org/3/library/fractions.html#fractions.Fraction.is_integer)
method to do so.
:::

We're on the home stretch now! We have the X/Y/Z velocities, and the starting
X/Y positions; the last thing we need is the starting Z position. That's nothing
we can't do with some simple algebra.

First, let's find the time $t$ at which some hailstone (e.g. "hailstone 1") and
the rock collide. (I'll be using a subscript $R$ to denote the rock.) At the
very least, their X positions will be equal at that time; once this equation is
written out in full, it's relatively simple to solve it for $t$.

$$
\begin{align*}
X_R(t) &= X_1(t) \\
x_R + t u_R &= x_1 + t u_1 \\
t u_R - t u_1 &= x_1 - x_R \\
t (u_R - u_1) &= x_1 - x_R \\
t &= \frac{x_1 - x_R}{u_R - u_1}
\end{align*}
$$

We also know that their Z positions will be equal. So we can solve this equation
for $z_R$ (the rock's starting Z position), which we'll be able to calculate now
that we know what $t$ is.

$$
\begin{align*}
Z_R(t) &= Z_1(t) \\
z_R + t w_R &= z_1 + t w_1 \\
z_R &= z_1 + t w_1 - t w_R \\
z_R &= z_1 + t (w_1 - w_R)
\end{align*}
$$

Let's write this out in code.

```py title="2023\day24\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        # Solve for the rock's Z position with some algebra
        time = (a.px - rpx) / (rvx - a.vx)
        rpz = a.pz + time * (a.vz - rvz)
        assert rpz.is_integer(), "rock's z position is not an integer"
        ...
```

Sweet! We now know everything there is to know about the rock: its X/Y/Z
velocity, _and_ its starting X/Y/Z positions!

---

And finally, the _very_ last thing to do is return the answer we want: the sum
of the rock's starting X, Y, and Z positions.

```py title="2023\day24\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        return int(rpx + rpy + rpz)
```

Boy oh boy, did this take a _lot_ of steps and a _lot_ of mental effort... but
I'm happy to say, we did eventually get there, and I'm proud of the work that
was put into our solution. Onward to Day 25!
