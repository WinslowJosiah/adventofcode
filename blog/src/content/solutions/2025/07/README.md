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
which _also_ has us modeling beams moving across a grid and splitting. I used a
`Direction` and `Position` class that day to represent beams, so I think it's a
good idea to use those classes again. Check out my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
to see how they're implemented, but the important things to know about them are:

- A `Direction` represents any of the four cardinal directions: up, down, left,
and right. They each have an `offset` property for working with `GridPoint`s
(i.e. row-column tuples), and they know how to `rotate()` themselves **C**lock**W**ise
(`"CW"`) or **C**ounter-**C**lock**W**ise (`"CCW"`).
- A `Position` represents a `GridPoint` that is facing in a `Direction`. It has
a `next_point` property which is the next point it sees in its facing direction,
and it knows how to `step()` forward and how to `rotate()` itself.

The rules for when a beam gets split are simpler than they were for 2023 Day 16,
so let's quickly implement them. The beam will unconditionally move forward, but
if the beam has moved over a splitter (`^`), it is split into two beams that
each step to the side and continue facing downwards.

```py title="2025\day07\solution.py"
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        next_beam = self.step()
        # Split beam at splitter; otherwise, continue forward
        if char == "^":
            return [
                next_beam.rotate("CW").step().rotate("CCW"),
                next_beam.rotate("CCW").step().rotate("CW"),
            ]
        return [next_beam]
```

Now let's parse the grid, and get our beam's starting position -- at the point
of the `S`, and moving down.

```py title="2025\day07\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        start = Beam(
            next(k for k, v in grid.items() if v == "S"),
            Direction.DOWN,
        )
        ...
```

We'll track the beams as they move and split using BFS ([breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)),
which will cause all of our beams to move downwards at pretty much the same
time. The general way to do a :abbr[BFS]{title="breadth-first search"} in Python
is with a [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque),
which allows for items to be efficiently appended and popped from both sides.
Throughout the search, we'll be popping beams from the left of the `deque` to
process them, and appending new beams to the right.

Any two beams in the exact same place will _merge together_, so we'll also keep
track of the beam positions we've seen before to prevent creating two beams with
the same position.

```py title="2025\day07\solution.py"
from collections import deque
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        # NOTE BFS is the best way to track the beams, as all beams will
        # be moving down at the same rate and won't lag behind.
        beams = deque([start])
        seen: set[Beam] = set()
        ...
```

From here, processing the beams is simple. For each "current" beam we process,
we take each possible "next" beam and have it continue downward until it leaves
the grid, or until it overlaps a beam position we've seen before. It's also very
simple to tally the splits as they happen; if there is more than one "next"
beam at any point, the "current" beam must have been split there.

```py title="2025\day07\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        num_splits = 0
        while beams:
            current_beam = beams.popleft()

            next_beams = current_beam.next_beams(grid[current_beam.point])
            # If the current beam has more than one possible next beam,
            # it has split
            if len(next_beams) > 1:
                num_splits += 1

            for next_beam in next_beams:
                if next_beam.point not in grid:
                    continue

                if next_beam in seen:
                    continue
                seen.add(next_beam)
                beams.append(next_beam)

        return num_splits
```

Our tally of splits will be our answer, and just like that, we're done with Part
1!

## Part 2

Turns out the beams are actually "quantum" particles. Whenever one is split, it
creates two parallel timelines: one in which the left path is taken, and one in
which the right path is taken. We're being asked to count how many different
timelines there are once the beams reach the bottom.

Besides the "quantum-ness" of the beams, their behavior is pretty much the same,
so I'll be solving both parts with a unified `solve` function today. For Part 2,
we just need a way to count the amount of timelines in which a given point is
reached. [`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter)
seems like the perfect data structure for this; we'll initialize a `timelines`
counter with one timeline at the starting point.

```py title="2025\day07\solution.py" ins="Counter, " ins="solve" ins="tuple[int, int]" ins={18-19}
from collections import Counter, deque
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        start = Beam(
            next(k for k, v in grid.items() if v == "S"),
            Direction.DOWN,
        )

        # NOTE BFS is the best way to track the beams, as all beams will
        # be moving down at the same rate and won't lag behind.
        beams = deque([start])
        seen: set[Beam] = set()

        num_splits = 0
        timelines = Counter([start.point])
        bottom_points: list[GridPoint] = []
        ...
```

I'll also use a list I call `bottom_points` to keep track of which points are
reached on the bottom of the grid.

Two additions need to be made within the main beam loop:

1. If any "next" beam ever leaves the grid, we want to track the "current" beam
that preceded it in our `bottom_points` list, since we care about the amount of
timelines that reached it.
2. Each "next" beam will be reached by every timeline that reached the "current"
beam, so we want to update the timeline count at the "next" beam's point.

```py title="2025\day07\solution.py" ins={9,11,14-16,23} ins=", num_bottom_timelines"
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        while beams:
            ...
            for next_beam in next_beams:
                # Track beam points as they leave the bottom
                if next_beam.point not in grid:
                    bottom_points.append(current_beam.point)
                    continue

                # This next beam's point has now been reached in all
                # timelines that have reached the current beam
                timelines[next_beam.point] += timelines[current_beam.point]

                if next_beam in seen:
                    continue
                seen.add(next_beam)
                beams.append(next_beam)

        num_bottom_timelines = sum(timelines[point] for point in bottom_points)
        return num_splits, num_bottom_timelines
```

Finally, the number of timelines that reached the bottom can be calculated with
a `sum` of a simple generator.

This gets us an answer in about 13.7 milliseconds on my machine -- not bad! But
can we do better?

### Bonus

When I shared the above solution [on Reddit](https://reddit.com/comments/1pg9w66/comment/nsqpjzk),
a user named `u/4HbQ`[^4hbq] asked me the following question:

[^4hbq]: His Advent of Code solutions are always very terse, and often contain
brilliant insights. He shares his solutions in the `r/adventofcode` subreddit
(instead of on GitHub or similar), and [his latest solution comment](https://reddit.com/comments/1pg9w66/comment/nspwfu4)
contains links to all of his 2025 solutions up to Day 7. I would definitely
recommend checking them out!

> Love your write-up (as usual!), but don't you think you're kind of
> overcomplicating things by using BFS and those classes?

For the most part, I write my solutions _before_ seeing anybody else's code, and
I avoid checking out other people's approaches unless I get stuck; after all, I
like the satisfaction of coming up with an approach _myself_. But sometimes my
first idea isn't my best; for a good example, see my [initial solution](https://github.com/WinslowJosiah/adventofcode/blob/3e7da8bc196cf422101f7512c41ef3516c735846/aoc/2023/day10/__init__.py)
versus my [new solution](https://github.com/WinslowJosiah/adventofcode/blob/main/solutions/2023/day10/solution.py)
to 2023 Day 10.

The `Position` class from my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
certainly offset my cognitive load -- I thought less about "how do I represent
these beams?" and more about "how do I manipulate these beams to get the
answers?". I think it's a good general abstraction for that reason, and that's
why my first thought today was to reach for that class.

But after checking out other people's solutions in [the Reddit megathread](https://reddit.com/comments/1pg9w66),
I found a somewhat common and pretty clever approach that avoids any such fancy
classes, and _doesn't even require thinking of the input as a grid_. I'll be
adapting that approach below.

---

As the beams move downward, they're not doing anything fancy: they're going down
each row, one by one, one beam (in multiple timelines) per column. This means we
can store beams/timeline counts in something like a `list` or a `dict`, with
each entry corresponding to one beam in one column, and updating the timeline
counts as we go down each row.

I'll go with a `list` for this, as it ends up being faster than using a `dict`.
We can quickly initialize a list of all zeros by multiplying `[0]` by the number
of entries we want, and then we can set the starting column as being reached in
one timeline so far.

```py title="2025\day07\solution.py"
class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        first_row, *last_rows = self.input
        start = first_row.index("S")

        num_splits = 0
        # Keep track of the number of timelines in which a beam reaches
        # each column
        timelines = [0] * len(first_row)
        timelines[start] = 1
        ...
```

Then, for each row after the first one, we update the beams/timeline counts. For
a beam-split to occur in a certain column, two things need to be true:

1. That column's character in the row is a splitter (`^`).
2. That column will be reached by _any_ timelines.

If those conditions aren't both true, we can ignore this column. Otherwise, the
beams there will have to split, which requires three steps:

1. To tally it, we add 1 to `num_splits`.
2. To perform the split, we add the timeline count of this column to the
timeline counts of the adjacent columns.
3. To prevent any beams from continuing down the same column, we zero out the
timeline count of this column.[^overwrite-timelines]

[^overwrite-timelines]: The one flaw with this approach as-is is that it would
overwrite some timelines if two splitters were directly next to each other. This
doesn't happen in the input, though, so that's okay.

    If we wanted to account for this, we could initialize a separate list to
    store the _new_ timeline states, and then only store them back to the
    _original_ timeline states after the row is done processing. I considered
    doing that anyway for the [purity](https://pep20.org/#practicality) of it --
    but again, this scenario doesn't happen in the input.

```py title="2025\day07\solution.py"
class Solution(StrSplitSolution):
        ...
        for row in last_rows:
            for col, char in enumerate(row):
                # The timelines will only change when any timeline
                # reaches a splitter
                if not (char == "^" and timelines[col]):
                    continue

                num_splits += 1
                # Split this column's timelines to both sides
                timelines[col - 1] += timelines[col]
                timelines[col + 1] += timelines[col]
                # No timelines will continue in this column
                # HACK This overwrites beams in the case of two adjacent
                # splitters, but that never happens in the input.
                timelines[col] = 0

        return num_splits, sum(timelines)
```

From there, we can return the number of splits for Part 1, and the sum of the
currently active timelines for Part 2.

This gets us an answer in about 0.57 milliseconds on my machine -- _24 times
faster_ than our previous approach -- and removes all dependencies! Very much
worth a revisit in my book.
