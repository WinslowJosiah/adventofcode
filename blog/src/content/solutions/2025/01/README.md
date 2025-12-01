---
year: 2025
day: 1
title: "Secret Entrance"
slug: 2025/day/1
pub_date: "2025-12-01"
# concepts: []
---
Hello, and welcome to [Advent of Code](https://adventofcode.com)! The AoC season
will be _much_ shorter starting this year -- 12 days, instead of 25 -- but that
doesn't mean it'll be any less fun!

Over the next 12 days, we'll be going through each puzzle one by one and walking
through a solution in Python. You don't need to know Python to understand or
apply the concepts, but you're expected to have at least _some_ base level of
programming knowledge to follow along; in any event, I'll do my best to explain
the relevant concepts as they come up.

If you're reading this for the first time, I'd recommend that you visit [the homepage](/)
so you know what to expect. And if you want to run these solutions directly,
I'll be pushing them to [my GitHub repo](https://github.com/WinslowJosiah/adventofcode)
as well.

That's all for now. Let's get coding!

## Part 1

We're rotating a dial on a combination lock. First, let's write a function to
parse the rotations we're doing; we'll return both the **direction** (`-1` or
`+1`, depending on which way we're rotating it) and the number of **clicks** to
rotate by.

```py title="2025\day01\solution.py"
def parse_rotation(line: str) -> tuple[int, int]:
    direction = -1 if line[0] == "L" else 1
    clicks = int(line[1:])
    return direction, clicks
```

After collecting the rotations, we can apply them to the dial (which starts at
50). What we're doing is going by some number of **clicks** in some
**direction** -- which we can convert into an offset simply by multiplying them
together. We can then use `%` (modulo) to keep the result between 0 and 99.

```py title="2025\day01\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        rotations = [parse_rotation(line) for line in self.input]
        dial = 50

        hits = 0
        for direction, clicks in rotations:
            # Rotate the dial
            dial = (dial + direction * clicks) % 100
            # If the dial is exactly 0, this is a hit
            if dial == 0:
                hits += 1

        return hits
```

We want to tally up the number of times the dial reaches 0 exactly. A pretty
easy start!

## Part 2

Looks like we need to rotate the dial more carefully. We want the number of
times it reaches 0 _at all_, not just the exact hits when each rotation ends.

This is no problem either; after all, we could just apply each rotation one
click at a time.

```py title="2025\day01\solution.py" ins="part_2" ins=/(passes) = 0/ ins=/\\* (1)/ ins=/(passes) \\+= 1/ ins=/return (passes)/ ins={10-11,13}
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        rotations = [parse_rotation(line) for line in self.input]
        dial = 50

        passes = 0
        for direction, clicks in rotations:
            for _ in range(clicks):
                # Rotate the dial by one click
                dial = (dial + direction * 1) % 100
                # If the dial is exactly 0, this is a pass
                if dial == 0:
                    passes += 1

        return passes
```

This _does_ work, and for my input it was pretty fast -- both parts ran in about
21 milliseconds on my machine. And if all you're after is an answer, this is
perfectly fine! But just for fun, let's see if there's a more _mathematical_
answer -- which would be more efficient for way larger amounts of clicks.

---

If we knew the dial started at 0 every single time, the number of 0-passes we'd
be able to do is simply the number of complete cycles we could do in that amount
of clicks -- in other words, `clicks // 100`. So what we could do is first
calculate how many clicks we'd need to get to 0, then use that formula on the
_rest_ of the clicks -- in other words, `(clicks - clicks_to_next_zero) // 100 + 1`[^plus-1].

[^plus-1]: Remember, we add 1 to represent the _first_ time we reach 0 during
the rotation!

So how many clicks would it take to get to 0?

- If we're going left, getting to 0 from $n$ would require $n$ clicks (or a full
100 clicks, if we're already starting at 0).
- If we're going right, getting to 0 from $n$ would require $100 - n$ clicks.

```py title="2025\day01\solution.py" ins="solve", ins="tuple[int, int]" ins={8,10-14}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        rotations = [parse_rotation(line) for line in self.input]
        dial = 50

        hits, passes = 0, 0
        for direction, clicks in rotations:
            # How many clicks do we need to pass the next 0?
            if direction < 0:
                clicks_to_next_zero = dial or 100
            else:
                clicks_to_next_zero = 100 - dial
            ...
```

:::tip
`a or b` returns `a` if `a` is considered true, and `b` otherwise. The number 0
is considered false, so in our case, `dial or 100` returns `dial` if `dial` is
nonzero, and `100` if `dial` is zero.

This is a neat way to give default values to variables, if you know you want to
do that when the left-hand side is considered false.
:::

Once we calculate this number and rotate the dial, we can do the logic for both
Parts 1 and 2 at the same time! We can add 1 to a tally of `hits` if 0 is
reached exactly, and we can use our formula from before to increase a tally of
`passes`.[^unnecessary-check]

[^unnecessary-check]: It turns out that checking `clicks >= clicks_to_next_zero`
is unnecessary; if the condition is untrue (i.e. no passes occur), the formula
will indeed evaluate to 0.

```py title="2025\day01\solution.py" ins={9-14,16}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
            # Rotate the dial
            dial = (dial + direction * clicks) % 100

            # If the dial is exactly 0, this is a hit
            if dial == 0:
                hits += 1
            # If we pass the next 0 at least once, tally up the passes
            if clicks >= clicks_to_next_zero:
                passes += (clicks - clicks_to_next_zero) // 100 + 1

        return hits, passes
```

We've achieved a pretty nice speedup; the solution now takes about 1 millisecond
to run on my machine. Compared to our previous time of 21 milliseconds, this may
not sound like a huge improvement... but if we were asked to rotate the dial by
(say) _millions_ of clicks, this approach would be able to handle that easily
without simulating each click. So I'd say this was worth it.

Overall, this wasn't too bad to solve... and we were even able to come up with a
smart speedup!
