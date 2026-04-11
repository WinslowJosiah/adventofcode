---
year: 2024
day: 1
title: "Historian Hysteria"
slug: 2024/day/1
pub_date: "2026-04-10"
# concepts: []
---
## Part 1

Happy 10th anniversary of Advent of Code!

My first Advent of Code was in 2023, and so I was excited to participate again
in 2024. By then I got a personal website, and so I decided to document my AoC
solution experience in [a series of blog posts](https://winslowjosiah.com/blog/2024/12/01/advent-of-code-2024-day-01).
If you want to see my original solutions and puzzle-solving experience, give
them a read.

Now that I'm presenting these solutions on a brand new site (even if the years
are going out of order), I've been adapting them to use a brand new solution
template -- a modified form of [David Brownman's template](https://github.com/xavdid/advent-of-code-python-template).
Some of the solutions I present will be cleaned-up forms of my original
solutions, and some will use different approaches and techniques I've seen from
others. And I hope you enjoy _all_ of them.

Let's get solving!

---

Each line has a pair of numbers, and we want to create two lists from them: one
with the numbers on the left, and one with the numbers on the right. We can do
this by unpacking every pair into the `zip` function like so:

```py
>>> pairs = [(3, 4), (4, 3), (2, 5), (1, 3), (3, 9), (3, 3)]
>>> list(zip(*pairs))
[(3, 4, 2, 1, 3, 3), (4, 3, 5, 3, 9, 3)]
```

To create each pair, we'll use [`str.split`](https://docs.python.org/3/library/stdtypes.html#str.split)
on a line of the input, and use the `int` function on the results to convert
them to integers. These pairs can then be unpacked into `zip` to give us our
left and right lists.

```py title="2024\day01\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        pairs = [tuple(int(n) for n in line.split()) for line in self.input]
        left, right = zip(*pairs)
        ...
```

In fact, it would be beneficial to create a _sorted_ version of the left and
right lists; after all, we'll want to pair together the smallest numbers from
both lists, the second smallest, the third smallest, etc. This can be easily
done with `sorted`.

```py title="2024\day01\solution.py" ins=/(\\[.*)zip\\(\\*pairs\\)(\\])/
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        pairs = [tuple(int(n) for n in line.split()) for line in self.input]
        left, right = [sorted(values) for values in zip(*pairs)]
        ...
```

Now each pair of numbers from the left and right lists can be iterated through
with `zip`. Adding up the distances (i.e. absolute differences) for all pairs
will give us our answer.

```py title="2024\day01\solution.py" ins={5}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        pairs = [tuple(int(n) for n in line.split()) for line in self.input]
        left, right = [sorted(values) for values in zip(*pairs)]
        return sum(abs(l - r) for l, r in zip(left, right))
```

We now have a solution in a (somewhat dense) 3 lines. Not bad.

## Part 2

Part 1 was pretty simple, and Part 2 looks to be even simpler! Thus, I'll be
using a unified `solve` function today.

Here, we'll need to take each number from the left list, and multiply it by the
number of times it appears in the right list. This sounds like a job for
[`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter).[^sequence-count]

[^sequence-count]: There exists the [`sequence.count`](https://docs.python.org/3/library/stdtypes.html#sequence.count)
method for counting items in a list, but it's more efficient to precalculate all
the item counts with `Counter` instead.

Once the counts of each item in the right list are calculated, each item in the
left list can simply be multiplied by its count in the right list and summed
together.

```py title="2024\day01\solution.py" ins={1,8-9} ins="total_distance =" ins="total_distance, similarity_score"
from collections import Counter

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        total_distance = sum(abs(l - r) for l, r in zip(left, right))

        right_counts = Counter(right)
        similarity_score = sum(l * right_counts[l] for l in left)

        return total_distance, similarity_score

```

In total, the solutions for both parts take up a manageable 6 lines. Again, not
too bad at all!
