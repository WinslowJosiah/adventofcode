---
year: 2025
day: 7
title: "Laboratories"
slug: 2025/day/7
pub_date: "2025-12-07"
# concepts: []
---
## Part 1

Another day, another grid puzzle. This is reminding me of [2023 Day 16](/solutions/2023/day/16),
which _also_ has us modeling beams moving across a grid and splitting.

That day, I used a `Direction` and `Position` class to represent beams -- and
initially, I used those same classes today as well. But when I posted my initial
solution [on Reddit](https://reddit.com/comments/1pg9w66/comment/nsqpjzk), a
user named `u/4HbQ`[^4hbq] noted that using those classes today would be
"overcomplicating things"... and in this case, I agree.

[^4hbq]: His Advent of Code solutions are always very terse, and often contain
brilliant insights. He shares his solutions in the `r/adventofcode` subreddit
(instead of on GitHub or similar), and [this solution comment of his](https://reddit.com/comments/1pkje0o/comment/ntlkg9i)
contains links to all of his 2025 solutions. I would definitely recommend
checking them out!

You can read my initial solution and writeup [on the Wayback Machine](https://web.archive.org/web/20251216191250/https://aoc.winslowjosiah.com/solutions/2025/day/7/)
for posterity. But here, I'll instead adapt a somewhat common and pretty clever
approach that avoids fancy custom classes, and _doesn't even require thinking of
the input as a grid_. (I _love_ that kind of solution.)

---

First, let's get the location of the `S` character in the first row -- i.e. the
starting position of our first beam.

```py title="2025\day07\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        first_row, *last_rows = self.input
        start = first_row.index("S")
        ...
```

As the beams move downward, they're not doing anything fancy: they're going down
each row, one by one, one beam per column. This means we can store beams in
something like a `list` or a `dict`, with each entry corresponding to one beam
in one column, and we can update the beam states as we go down each row.

I'll go with a `list` for this, as it ends up being faster than using a `dict`.
We can quickly initialize a list that repeats a single item using list
multiplication; we'll want a list of all `False` values. And of course, we'll
want to tally the number of splits, so we'll initialize our `num_splits`
variable to 0.

```py title="2025\day07\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        num_splits = 0
        # Keep track of whether a beam is in each column
        beams = [False] * len(first_row)
        beams[start] = True
        ...
```

Now we'll update the beams for each row after the first one. For a beam-split to
occur in a certain column, two things need to be true:

1. That column's character in the row is a splitter (`^`).
2. That column will be reached by a beam.

If those conditions aren't both true, we can ignore this column. Otherwise, the
beams there will have to split, which requires three steps:

1. To tally it, we add 1 to `num_splits`.
2. To perform the split, we copy this column's beam to the adjacent columns.
3. To prevent the split beam from continuing down the same column, we store a
value of `False` for this column's beam.[^overwritten-beams]

[^overwritten-beams]: The one flaw with this approach as-is is that some beams
would be overwritten if two splitters were directly next to each other. This
doesn't happen in the input, though, so that's okay.

    If we wanted to account for this, we could initialize a separate list to
    store the _new_ beam states, and then only store them back to the
    _original_ beam states after the row is done processing. I considered doing
    that anyway for the [purity](https://pep20.org/#practicality) of it -- but
    again, this scenario doesn't happen in the input.

```py title="2025\day07\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        for row in last_rows:
            for col, char in enumerate(row):
                # The beam states will only change when a beam reaches a
                # splitter
                if not (char == "^" and beams[col]):
                    continue

                num_splits += 1
                # Split this column's beam to both sides
                beams[col - 1] = beams[col]
                beams[col + 1] = beams[col]
                # No beam will continue in this column
                # HACK This overwrites beams in the case of two adjacent
                # splitters, but that never happens in the input.
                beams[col] = False

        return num_splits
```

From there, we can simply return the number of splits.

## Part 2

Turns out the beams are actually "quantum" particles. Whenever one is split, it
creates two parallel timelines: one in which the left path is taken, and one in
which the right path is taken. We're being asked to count how many different
timelines there are once the beams reach the bottom.

Besides the "quantum-ness" of the beams, their behavior is pretty much the same,
so I'll be solving both parts with a unified `solve` function today.

We just need a way to count the amount of timelines in which a given column is
reached. For this, we can rework our `beams` list to store _beam counts_ instead
of simple `True`/`False` values. This requires a few changes:

1. We want to initialize the `beams` list with all 0s -- except for the starting
beam's column, which is initialized with a 1.
2. When a beam is split, we want to _add_ this column's beam counts to the
adjacent columns. (If we were to still _copy_ the beam counts, the existing
beams would be overwritten and lost.)
3. To stop a split beam from continuing down its original column, we want to
store 0 there instead of `False`.

```py title="2025\day07\solution.py" ins="solve" ins="tuple[int, int]" ins="the number of beams" ins=/\\[(0)\\]/ ins=/beams\\[start\\] = (1)/ ins=/(\\+=) beams\\[col\\]/ ins=/beams\\[col\\] = (0)/ ins=", sum(beams)"
class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        first_row, *last_rows = self.input
        start = first_row.index("S")

        num_splits = 0
        # Keep track of the number of beams in each column
        beams = [0] * len(first_row)
        beams[start] = 1

        for row in last_rows:
            for col, char in enumerate(row):
                # The beam states will only change when a beam reaches a
                # splitter
                if not (char == "^" and beams[col]):
                    continue

                num_splits += 1
                # Split this column's beam to both sides
                beams[col - 1] += beams[col]
                beams[col + 1] += beams[col]
                # No beam will continue in this column
                # HACK This overwrites beams in the case of two adjacent
                # splitters, but that never happens in the input.
                beams[col] = 0

        return num_splits, sum(beams)
```

Part 2's solution then becomes the sum of all the beam counts! Nice and simple.
