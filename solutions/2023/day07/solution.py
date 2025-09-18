# https://adventofcode.com/2023/day/7

from collections import Counter

from ...base import StrSplitSolution, answer


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


def tiebreaker(hand: str, card_values: str) -> tuple[int, ...]:
    return tuple(card_values.index(c) for c in hand)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 7.
    """
    _year = 2023
    _day = 7

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

    @answer(250957639)
    def part_1(self) -> int:
        return self._solve(joker=False)

    @answer(251515496)
    def part_2(self) -> int:
        return self._solve(joker=True)
