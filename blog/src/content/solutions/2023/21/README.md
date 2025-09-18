---
year: 2023
day: 21
title: "Step Counter"
slug: 2023/day/21
pub_date: "2025-11-13"
# concepts: []
---
## Part 1

Another day, another grid puzzle. Today, we're taking a leisurely walk in a
large garden. What could go wrong?

As always, we will first parse the grid. Here I'm ignoring the `#` characters,
so the only tiles in the grid will be the ones we can walk on.

```py title="2023\day21\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        ...
```

We want to know which tiles can be reached after walking a certain distance from
the start. This sounds like a perfect application of [:abbr[BFS]{title="breadth-first search"}](https://en.wikipedia.org/wiki/Breadth-first_search).
We'll use a `deque` to keep track of the tiles we're currently walking on, and a
`set` to keep track of tiles we've visited (because we actually never need to
visit them twice). I use the `neighbors` function I introduced on [Day 10](/solutions/2023/day/10)
to get the neighbors of a tile, and if it's still in the grid (i.e. not a `#`),
I append it to the `deque`.

```py title="2023\day21\solution.py"
from collections import deque

def num_paths(grid: Grid[str], path_length: int) -> int:
    start = next(k for k, v in grid.items() if v == "S")
    visited: dict[GridPoint, int] = {}
    queue: deque[tuple[int, GridPoint]] = deque([(0, start)])
    while queue:
        distance, point = queue.popleft()
        if point in visited or distance > path_length:
            continue
        visited[point] = distance

        for n in neighbors(point, num_directions=4):
            if n in grid:
                queue.append((distance + 1, n))

    # NOTE If a point's distance has the same parity as the path length,
    # it can be reached through some amount of doubling back.
    return sum(v % 2 == path_length % 2 for v in visited.values())
```

Note that we can end our path at any tile with an even number of steps before
the path ends -- we can just move back and forth repeatedly from a neighboring
tile for the rest of our steps. So our path can end at any tile where the parity
(evenness/oddness) of the distance to them is the same as the parity of the path
length we want; this is what that `sum` expression tallies up.

How many tiles would we reach after 64 steps? Only one way to find out: call the
function for it.

```py title="2023\day21\solution.py" ins={6}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        return num_paths(grid, 64)
```

Now we can stroll over to Part 2.

## Part 2

Looks like our leisurely walk just got longer. So long, in fact, that
brute-forcing the answer is entirely impractical. So what do we do next?

Well, when I first saw this puzzle, I didn't know what to do next. I usually
look at [the Reddit solution thread](https://reddit.com/comments/18nevo3) in
this scenario, but it didn't help much this time. Most people went with some
sort of [geometric solution](https://github.com/villuna/aoc23/wiki/A-Geometric-solution-to-advent-of-code-2023,-day-21)
I honestly didn't understand; when I tried coding such a solution -- even when I
copy-pasted other people's code for it -- I got a wrong answer every time.

This is what led me to really _hate_ this puzzle back then. I hated it so much,
I said so forcefully in [a long comment](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2023/day21/__init__.py#L76-L85)
in my solution file. Not only was this in a genre of puzzle I dislike -- one
which requires you to notice some non-trivial features of the puzzle input[^not-in-example-input]
-- but even noticing those features didn't seem to work. I was at a complete loss.

[^not-in-example-input]: And those features are definitely _not_ in the example
input!

Luckily, some people used an alternate approach that _did_ work for me. And with
the benefit of hindsight, let me present it in a way that I feel like I could've
discovered myself.

---

First order of business: modifying the path-counting function to handle an
infinitely-wrapping grid. We can use the `%` (modulo) operator to make the
coordinates wrap once they get beyond the bounds of the grid, and we'll want to
check if this "wrapped" point is in the grid to see if we can walk on it.

```py title="2023\day21\solution.py" ins="grid_size: int, " ins=/if (n_wrapped)/ ins={8}
...

def num_paths(grid: Grid[str], grid_size: int, path_length: int) -> int:
    ...
    while queue:
        ...
        for n in neighbors(point, num_directions=4):
            n_wrapped = n[0] % grid_size, n[1] % grid_size
            if n_wrapped in grid:
                queue.append((distance + 1, n))
    ...
```

We should also modify our Part 1 solution to account for this. 64 steps still
leaves us within the bounds of the grid, so this won't affect our answer.

```py title="2023\day21\solution.py" ins="solve" ins="tuple[int, int]" ins="grid_size, " ins="num_short_paths =" ins={5-6}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        assert len(self.input) == len(self.input[0]), "not a square grid"
        grid_size = len(self.input)
        grid = parse_grid(self.input, ignore_chars="#")

        num_short_paths = num_paths(grid, grid_size, 64)
        ...
```

The key to our solution is noticing two things about the input:

1. The middle column and middle row (which you start at the intersection of) are
completely empty. So the farthest you could travel horizontally or vertically
would be by walking straight along that row or column.
2. The number of steps you're asked to walk is highly specific: **26,501,365**.
This is exactly **202,300 times 131 (the grid size), plus 65**.[^202300] Walking
65 steps straight will bring us to the exact edge of the garden; walking the
rest of the way will bring us to the edge of the 202,300th garden plot out.

[^202300]: Yes, the factor of **2023**00 [was intentional](https://reddit.com/comments/18nx8de/comment/kedjwqd).

So the farthest outward we can walk is along a whole number of garden plots.
Let's write some code to verify this.

```py title="2023\day21\solution.py" ins={6-12}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        # NOTE The middle row and column happen to be blank, so taking a
        # straight path should bring us directly onto the edge of one of
        # the infinitely-repeating garden plots. n is the maximum number
        # of garden plots outward that we can traverse.
        NUM_STEPS = 26501365
        n, remainder = divmod(NUM_STEPS - grid_size // 2, grid_size)
        assert remainder == 0, "radius isn't whole number of garden plots"
        ...
```

If this assumption were wrong, we would get an error message. But we don't, so
we're in the clear.

Perhaps we can come up with a formula for our answer based on the number of
garden plots we'll be traversing. Let's calculate some small results and see
what they look like as the number of plots gets bigger.

```py title="2023\day21\solution.py"
...

class Solution(StrSplitSolution):
    def _debug_num_paths(self):
        assert len(self.input) == len(self.input[0]), "not a square grid"
        grid_size = len(self.input)
        grid = parse_grid(self.input, ignore_chars="#")

        for plots in range(10):
            steps = plots * grid_size + grid_size // 2
            paths = num_paths(grid, grid_size, steps)
            print(f"{plots} plot(s) ({steps} steps): {paths}")
```

Here's the output I get (the numbers will be different for your input):

```text
0 plot(s) (65 steps): 3802
1 plot(s) (196 steps): 33732
2 plot(s) (327 steps): 93480
3 plot(s) (458 steps): 183046
4 plot(s) (589 steps): 302430
5 plot(s) (720 steps): 451632
6 plot(s) (851 steps): 630652
7 plot(s) (982 steps): 839490
8 plot(s) (1113 steps): 1078146
9 plot(s) (1244 steps): 1346620
```

One useful way to identify an unknown sequence is to get the differences between
terms, the differences between those differences, and so on, and see if you can
spot a pattern. Here's what I get for the "first differences" (between terms)
and the "second differences" (between the first differences).

| Plots | Paths     | First Diffs | Second Diffs |
| ----- | --------- | ----------- | ------------ |
| 0     | 3,802     | 29,930      | 29,818       |
| 1     | 33,732    | 59,748      | 29,818       |
| 2     | 93,480    | 89,566      | 29,818       |
| 3     | 183,046   | 119,384     | 29,818       |
| 4     | 302,430   | 149,202     | 29,818       |
| 5     | 451,632   | 179,020     | 29,818       |
| 6     | 630,652   | 208,838     | 29,818       |
| 7     | 839,490   | 238,656     | 29,818       |
| 8     | 1,078,146 | 268,474     | ...          |
| 9     | 1,346,620 | ...         | ...          |

The second differences are all the same! That means that this sequence can be
described by a [quadratic function](https://en.wikipedia.org/wiki/Quadratic_function).
And crucially, we can figure out what that function _is_ using only the first
three terms -- enough to tell us what the constant second difference is.

Let's call the result of plugging $n$ into our function $f(n)$; so $f(0)$,
$f(1)$, and $f(2)$ are the results of plugging in 0, 1, and 2 respectively. We
want to find the quadratic function $f(n) = an^2 + bn + c$ that gives us our
sequence of path counts.

When we plug in 0, we notice something helpful: $f(0)$ is exactly the value of
$c$.

$$
f(0) = c
$$

And when we calculate the second difference (i.e. the difference between
differences), we notice something else helpful: the second difference is exactly
twice the value of $a$. So the value of $a$ will be the second difference
($= f(2) - 2f(1) + f(0)$) divided by 2.

$$
\begin{align*}
  (\Delta f)(0) &= f(1) - f(0) \\
                &= (a + b + c) - (c) \\
                &= a + b \\
\\
  (\Delta f)(1) &= f(2) - f(1) \\
                &= (4a + 2b + c) - (a + b + c) \\
                &= 3a + b \\
\\
(\Delta^2 f)(0) &= (\Delta f)(1) - (\Delta f)(0) \\
                &= (3a + b) - (a + b) \\
                &= 2a
\end{align*}
$$

:::note
$(\Delta f)$ is the first-differences function, and $(\Delta^2 f)$ is the
second-differences function. Don't be scared; this is just the standard
mathematical notation.
:::

Lastly, the difference between the first two terms (i.e. the first first
difference, or $f(1) - f(0)$) happens to equal $a + b$. So subtracting the value
of $a$ from this will give us the value of $b$.

$$
\begin{align*}
    f(1) - f(0) &= (a + b + c) - (c) \\
                &= a + b \\
f(1) - f(0) - a &= b
\end{align*}
$$

We now have all three of our coefficients!

$$
\begin{align*}
a &= \frac{f(2) - 2f(1) + f(0)}{2} \\
b &= f(1) - f(0) - a \\
c &= f(0)
\end{align*}
$$

A simple generator expression can be used to get $f(0)$, $f(1)$, and $f(2)$, and
the formulas we just found can be used to get the coefficients $a$, $b$, and
$c$. Using those coefficients to calculate $an^2 + bn + c$ is our last step.

```py title="2023\day21\solution.py" ins={6-20}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        # HACK Traversing outward by whole numbers of garden plots leads
        # to results that happen to follow a quadratic curve. Using some
        # algebra, we can derive the coefficients of that curve from the
        # results of traversing 0, 1, and 2 garden plots. We can then
        # directly calculate the result of traversing n garden plots.
        f0, f1, f2 = (
            num_paths(grid, grid_size, plots * grid_size + grid_size // 2)
            for plots in range(3)
        )
        a = (f2 - 2 * f1 + f0) / 2
        b = f1 - f0 - a
        c = f0
        num_long_paths = round(a * n ** 2 + b * n + c)

        return num_short_paths, num_long_paths
```

After a bit of a... _long walk_...[^bad-pun] we finally arrive at our answer. I
still don't particularly like the way we got it, but at least now I can say I
have a correct solution that I fully understand. And now you can too!

[^bad-pun]: Bad pun, I know.
