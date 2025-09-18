---
year: 2023
day: 7
title: "Camel Cards"
slug: 2023/day/7
pub_date: "2025-10-15"
# concepts: []
---
## Part 1

We've got an in-universe game called Camel Cards, a simplified version of poker.
We could try and pull the relevant parts from some pre-existing poker evaluation
function, but we don't need to; the counts of each card are all we need to
identify the hands.

| Counts (High to Low) | Poker Hand      |
| -------------------- | --------------- |
| `(5,)`               | Five of a kind  |
| `(4, 1)`             | Four of a kind  |
| `(3, 2)`             | Full house      |
| `(3, 1, 1)`          | Three of a kind |
| `(2, 2, 1)`          | Two pair        |
| `(2, 1, 1, 1)`       | One pair        |
| `(1, 1, 1, 1, 1)`    | High card       |

If we sort the counts of each card from highest to lowest (as I did in the above
table), we notice two things:

1. Each set of counts corresponds to a unique poker hand type. For example, any
group of cards with **3** of one and **2** of the other (e.g. `23332`, `77888`,
etc.) is a **full house**.
2. Thanks to [lexicographical ordering](https://docs.python.org/3/tutorial/datastructures.html#comparing-sequences-and-other-types),
these counts will literally be considered _greater_ if they correspond to better
poker hands. For example, `(5,)` (five of a kind) is greater than `(4, 1)` (four
of a kind), which is greater than `(3, 2)` (full house), etc.

This means that the following function is all we need in order to rank hands!

```py title="2023\day07\solution.py"
from collections import Counter

def rank_hand(hand: str) -> tuple[int, ...]:
    # NOTE Sorting the counts of each card in descending order just so
    # happens to give a correct ranking of hands.
    hand_values: list[int] = sorted(Counter(hand).values(), reverse=True)
    return tuple(hand_values)
```

But if two hands have the same type, a tiebreaker rule is used, based on the
relative strengths of each card in line (`A` being highest, `2` being lowest).
This can also be pretty terse; thanks to lexicographical ordering (again), we
can just convert each card to its numeric strength value using [`str.index`](https://docs.python.org/3/library/stdtypes.html#str.index).

```py title="2023\day07\solution.py"
def tiebreaker(hand: str) -> tuple[int, ...]:
    return tuple("23456789JQKA".index(c) for c in hand)
```

The hands should be sorted from worst to best, so we'll collect them in a list
called `scored_hands` and use [`sorted`](https://docs.python.org/3/library/functions.html#sorted)
to loop through a sorted version. The values we'll append to `scored_hands` will
be tuples containing three items in this order: the ranked hand type, the
tiebreaker, and the bid amount.[^sorted-bid] Thanks to lexicographical ordering
(yet again), this will correctly order the hands.

[^sorted-bid]: We don't want to sort by the bid -- and in fact, if we use the
`key` keyword argument of `sorted`, we wouldn't have to -- but we can get away
with it because each of the hands happen to be unique.

```py title="2023\day07\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        scored_hands: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
        for line in self.input:
            hand, bid = line.split()
            scored_hands.append((rank_hand(hand), tiebreaker(hand), int(bid)))

        return sum(
            rank * bid
            for rank, (_, _, bid) in enumerate(sorted(scored_hands), start=1)
        )
```

A quick `sum` (using `enumerate` to get the hands' ranks) will solve this
puzzle.

## Part 2

`J` is going to become the Joker. Other than that, not a lot will change from
Part 1 to Part 2, so we can factor out the entire solution into a function, and
change what happens in it based on a parameter.

```py title="2023\day07\solution.py" ins={4,8,10-11}
...

class Solution(StrSplitSolution):
    def _solve(self, joker: bool) -> int:
        ...  # Part 1 code from before

    def part_1(self) -> int:
        return self._solve(joker=False)

    def part_2(self) -> int:
        return self._solve(joker=True)
```

How do we assign the jokers so we get the best possible hand? Well, as before,
the most important number in our `rank_hand` result is the largest one (the
amount of the most common card). So the best strategy turns out to be assigning
every joker to whatever the most common other card is.

```py title="2023\day07\solution.py" ins={6-10} ins=", joker: bool"
def rank_hand(hand: str, joker: bool) -> tuple[int, ...]:
    # NOTE Sorting the counts of each card in descending order just so
    # happens to give a correct ranking of hands.
    hand_values: list[int] = sorted(Counter(hand).values(), reverse=True)

    # If using the joker (and the joker isn't in a five-of-a-kind),
    # consider the joker as whatever the most common other card is
    if joker and 0 < (num_jokers := hand.count("J")) < 5:
        hand_values.remove(num_jokers)
        hand_values[0] += num_jokers

    return tuple(hand_values)
```

We only do these joker shenanigans if we need to, and if the number of jokers is
more than 0. (I also check that the number of jokers is less than 5, because
this snippet would break if we had 5 jokers and removed them all before adding
them back.)

The `tiebreaker` function also needs to be changed to reflect the new card
strengths. The cards in their proper order can simply be a parameter.

```py title="2023\day07\solution.py" ins=", card_values: str" ins="card_values"
def tiebreaker(hand: str, card_values: str) -> tuple[int, ...]:
    return tuple(card_values.index(c) for c in hand)
```

Last but not least, we need to pass in our joker preference and card-value
ordering to these altered functions.

```py title="2023\day07\solution.py" ins={5} ins=", joker=joker" ins=", card_values"
...

class Solution(StrSplitSolution):
    def _solve(self, joker: bool) -> int:
        card_values = "J23456789TQKA" if joker else "23456789TJQKA"

        scored_hands: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
        for line in self.input:
            hand, bid = line.split()
            scored_hands.append(
                (
                    rank_hand(hand, joker=joker),
                    tiebreaker(hand, card_values),
                    int(bid),
                )
            )

        return sum(
            rank * bid
            for rank, (_, _, bid) in enumerate(sorted(scored_hands), start=1)
        )

    ...
```

Pretty painless overall, especially compared to what I was expecting.
