---
year: 2023
day: 4
title: "Scratchcards"
slug: 2023/day/4
pub_date: "2025-10-10"
# concepts: []
---
## Part 1

Looks like we have to count how many numbers are shared between two halves of a
scratchcard. We should first figure out how to do this.

It's a simple matter to get both halves of the scratchcard -- no regex needed
this time. And to count the matches, we can convert both scratchcard halves to
sets, use [the `&` operator](https://docs.python.org/3/library/stdtypes.html#frozenset.intersection)
(set intersection) to get the numbers in common, and get the `len` of the
result.

```py title="2023\day04\solution.py"
def num_matching_numbers(line: str) -> int:
    _, rest = line.split(":")
    winners, nums = rest.split("|")
    # Count only the numbers in common between both lists
    return len(set(winners.split()) & set(nums.split()))
```

Once we know how many matches we have, we must use that to calculate the points
we've earned. 0 matches earns us 0 points; otherwise, the first match earns us 1
point, and every match after that doubles our points. This pattern exactly
matches the powers of 2; we just need to subtract 1 from the exponent, and use
`int()` to have 0 matches result in 0 points instead of 0.5 points.

| # of matches ($m$) | # of points | $2 ^ {m - 1}$ |
| :----------------: | :---------: | :-----------: |
|         0          |      0      |      0.5      |
|         1          |      1      |       1       |
|         2          |      2      |       2       |
|         3          |      4      |       4       |
|         4          |      8      |       8       |
|         5          |     16      |      16       |
|        ...         |     ...     |      ...      |

This leads to a fairly simple comprehension inside of a `sum`.

```py title="2023\day04\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(
            int(2 ** (num_matching_numbers(line) - 1))
            for line in self.input
        )
```

## Part 2

Apparently winning on scratchcards doesn't earn you points, but only _more_
scratchcards? Sounds pointless, but let's figure this out anyway.

First, let's use a `defaultdict(int)` to keep track of how many copies of each
card we have. At the end, we'll count our scratchcards by summing up the values
we kept track of.

```py title="2023\day04\solution.py"
from collections import defaultdict

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        num_cards: dict[int, int] = defaultdict(int)
        for card_id, line in enumerate(self.input, start=1):
            num_matches = num_matching_numbers(line)

            ...  # TODO Add win-more-scratchcards code

        return sum(num_cards.values())
```

There are only two ways to earn scratchcards:

1. By starting out with that scratchcard. (Each initial scratchcard counts as
one scratchcard!)
2. By winning it from a match on a previous card.

Let's say you've found $m$ matching numbers on scratchcard number $c$; the _IDs_
of the cards you've won will be the next $m$ cards in line (from $c + 1$ to
$c + m$), and the number of _copies_ you get of each of these cards will be
however many copies you have of card $c$. (The wording of the prompt is a bit
confusing, but that's as simple as I could describe it!)

```py title="2023\day04\solution.py" ins={11-16}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        num_cards: dict[int, int] = defaultdict(int)
        for card_id, line in enumerate(self.input, start=1):
            num_matches = num_matching_numbers(line)

            # You start with 1 of this scratchcard
            num_cards[card_id] += 1
            # For each copy of this scratchcard, a copy of each of the
            # next `num_matches` scratchcards is won
            for c in range(card_id + 1, card_id + num_matches + 1):
                num_cards[c] += num_cards[card_id]

        return sum(num_cards.values())
```

Once the rules are clarified to that level of precision, implementing them is
straightforward, and the resulting code is pretty terse!
