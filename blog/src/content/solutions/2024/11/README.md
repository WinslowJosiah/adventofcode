---
year: 2024
day: 11
title: "Plutonian Pebbles"
slug: 2024/day/11
pub_date: "2026-05-29"
# concepts: []
---
## Part 1

We have a line of stones that change every time you blink. We'll want to create
a function to model how each stone changes after each blink; because the result
could be one or two stones, it feels natural to use a simple [generator function](https://realpython.com/introduction-to-python-generators/).
The result of a blink will be one of three things:

- If the stone is `0`, we yield `1` and return.
- If the stone is a number with an _even_ number of digits, we convert the
number to a string, split it in half, and yield each half as a number. (Then we
return, of course.)
- If the other rules didn't apply, we yield the stone multiplied by 2024 and
return.

```py title="2024\day11\solution.py"
from collections.abc import Iterator

def blink(stone: int) -> Iterator[int]:
    # 0 turns to 1
    if stone == 0:
        yield 1
        return

    # If the digit string can be split in half, it turns to both halves
    digits = str(stone)
    half_length, remainder = divmod(len(digits), 2)
    if remainder == 0:
        yield int(digits[:half_length])
        yield int(digits[half_length:])
        return

    # Any other number n turns to n * 2024
    yield stone * 2024
    return
```

Using this generator, we can actually simulate a blink for every stone fairly
easily with a list comprehension (but we have to be careful with the order of
the `for` portions). And to simulate _25_ blinks, we can simply put that list
comprehension in a `for` loop.

```py title="2024\day11\solution.py"
...

class Solution(IntSplitSolution):
    separator = " "

    def part_1(self) -> int:
        stones = self.input

        for _ in range(25):
            stones = [
                new_stone
                for stone in stones
                for new_stone in blink(stone)
            ]

        return len(stones)
```

The amount of stones in our list by the end is the answer we're after.
Suspiciously simple...

## Part 2

The only change from Part 1 is that, instead of blinking 25 times, we're
blinking _75_ times. On paper, we could use the same process as before with a
different number, so let's factor it out before we do anything.

```py title="2024\day11\solution.py" ins=/def (_solve)/ ins=", blinks: int" ins=/\\((blinks)\\)/ ins={18-22}
...

class Solution(IntSplitSolution):
    separator = " "

    def _solve(self, blinks: int) -> int:
        stones = self.input

        for _ in range(blinks):
            stones = [
                new_stone
                for stone in stones
                for new_stone in blink(stone)
            ]

        return len(stones)

    def part_1(self) -> int:
        return self._solve(25)

    def part_2(self) -> int:
        return self._solve(75)
```

But we quickly run into a problem. Even though Part 1 finishes in less time than
it takes to blink _once_ in real life... let's just say, Part 2 will take us
_way_ more than 75 IRL blinks to finish this way. So how can we make it finish
faster?

When I was first solving this puzzle, coming up with a better approach took me
way longer than I'm willing to admit. And I attribute that to _this_ specific
sentence in the original prompt:

> No matter how the stones change, their **order is preserved**, and they stay
> on their perfectly straight line.

The emphasis there isn't mine. The prompt renders the words "**order is
preserved**" in a glowing white. So it _must_ be important to store every single
stone in its original order, right? Nope; the order of the stones affects
_nothing_ about the answer or the blinking process, so that detail is a
[red herring](https://en.wikipedia.org/wiki/Red_herring).

The only thing that will affect our answer is how many of each stone we have.
Luckily, Python's `collections` module has a datatype for keeping track of item
counts: the aptly-named [`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter).
So instead of a list, let's use a `Counter` to store the stones.

```py title="2024\day11\solution.py" del={7} ins={1,8-10}
from collections import Counter
...

class Solution(IntSplitSolution):
    ...
    def _solve(self, blinks: int) -> int:
        stones = self.input
        # NOTE We can get away with only storing stone counts. Despite
        # the prompt saying "order is preserved", order does not matter.
        stones = Counter(self.input)
        ...
```

During each blink, we can also update a new `Counter` with the post-blink
stones; for each new stone that results from the blink, we'll add the original
stone's count to the new count of that new stone. And once every blink is done,
we can return the total count of stones.

```py title="2024\day11\solution.py" ins={11-15} ins="stones.total()"
...

class Solution(IntSplitSolution):
    ...
    def _solve(self, blinks: int) -> int:
        # NOTE We can get away with only storing stone counts. Despite
        # the prompt saying "order is preserved", order does not matter.
        stones = Counter(self.input)

        for _ in range(blinks):
            new_stones: Counter[int] = Counter()
            for stone, count in stones.items():
                for new_stone in blink(stone):
                    new_stones[new_stone] += count
            stones = new_stones

        return stones.total()
```

Effectively, we are processing many copies of a stone all at once instead of
individually; _this_ is the insight that speeds up our solution. In the end,
both parts end up taking ~80 milliseconds to finish on my machine -- _literally_
in the blink of an eye!
