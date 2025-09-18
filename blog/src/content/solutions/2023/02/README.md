---
year: 2023
day: 2
title: "Cube Conundrum"
slug: 2023/day/2
pub_date: "2025-10-08"
# concepts: [regex]
---
## Part 1

Would you like to play a game?

We're given some information from several games, in which a number of random
cubes were drawn from a bag. The bag is assumed to contain 12 red cubes, 13
green cubes, and 14 blue cubes. Let's define that first.

```py title="2023/day02/solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        BAG = {"red": 12, "green": 13, "blue": 14}
        ...
```

We need to loop through every game along with their IDs (starting from 1). This
can be done using [`enumerate`](https://docs.python.org/3/library/functions.html#enumerate)
and its optional second argument (the starting value).

The general outline of the solution will look something like this, where we add
the game ID to a running total if the game is possible. We just need to know
what to write for that condition.

```py title="2023/day02/solution.py" "()"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        total = 0
        for game_id, game in enumerate(self.input, start=1):
            _, cubes = game.split(": ")

            if ():  # TODO Add is-game-possible check
                total += game_id

        return total
```

Here, our `cubes` string will look something like `3 blue, 4 red; 1 red, 2
green, 6 blue; 2 green`. The relevant information for each draw of cubes is the
number and color.

:::note
Even though the `cubes` string has both semicolons and commas as separators, it
turns out that you _don't_ need to differentiate between them. The only thing
that matters is the number and color of each set of drawn cubes.
:::

A simple regex that can detect the number and color is `(\d+) (\w+)` (which you
can test [here at regex101](https://regex101.com/r/4pnKWQ/1)). The meaning of
each segment is as follows:

- `(\d+)`: One or more (`+`) of any digit (`\d`), saved in a "capturing group"
(`(...)`).
- ` `: A literal space character.
- `(\w+)`: One or more (`+`) of any letter/number (`\w`), saved in a "capturing
group" (`(...)`).

```py
>>> import re
>>> pattern = r"(\d+) (\w+)"
>>> cubes = "3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"
>>> re.findall(pattern, cubes)
[('3', 'blue'),
 ('4', 'red'),
 ('1', 'red'),
 ('2', 'green'),
 ('6', 'blue'),
 ('2', 'green')]
```

For each draw to be possible, the number of cubes must be no more than the bag's
count for that color. We can loop a simple comparison over every draw, and check
that every comparison works using [`all`](https://docs.python.org/3/library/functions.html#all)
(which checks whether all values in an iterable are true).

```py title="2023/day02/solution.py" ins={1,11-16}
import re

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        BAG = {"red": 12, "green": 13, "blue": 14}

        total = 0
        for game_id, game in enumerate(self.input, start=1):
            _, cubes = game.split(": ")

            # This game is possible if all cube counts are within the
            # given cube counts of the bag
            if all(
                int(count) <= BAG[color]
                for count, color in re.findall(r"(\d+) (\w+)", cubes)
            ):
                total += game_id

        return total
```

## Part 2

This time, instead of being given the contents of the bag, we have to figure it
out. Or at least, figure out the _minimum_ contents of the bag.

We have to keep track of the minimum number of each color cube that could
possibly be in the bag. [`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
is a good choice of data structure for this; it's like the `dict` we used to
store the bag in Part 1, except getting a nonexistent value won't raise a
`KeyError`.

```py
>>> from collections import defaultdict
>>> min_bag = defaultdict(int)
>>> min_bag["red"] = 4
>>> min_bag["red"]
4
>>> min_bag["green"]
0
```

:::tip
The `defaultdict` constructor takes a "factory function", which it calls to
populate an item if it doesn't exist.

In this case, the "factory function" we used is `int`; calling `int()` without
arguments gives the default value of `0`.
:::

Our loop over all the games can be simplified, because we no longer need the
game ID. As for the minimum-bag, the number of each color cube should be the
largest number of cubes in any draw of that color.

```py title="2023/day02/solution.py" ins={1-2,14-18,20} del={10}
from collections import defaultdict
from math import prod
import re

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        total = 0
        for game_id, game in enumerate(self.input, start=1):
        for game in self.input:
            _, cubes = game.split(": ")

            # The minimum amount of each cube is however many of that
            # cube were drawn in the biggest draw
            min_bag: dict[str, int] = defaultdict(int)
            for count, color in re.findall(r"(\d+) (\w+)", cubes):
                min_bag[color] = max(min_bag[color], int(count))

            total += prod(min_bag.values())

        return total
```

Once the minimum-bag is found, the product of its values can be found with
[`math.prod`](https://docs.python.org/3/library/math.html#math.prod). We add
these results to a running total, just like Part 1.
