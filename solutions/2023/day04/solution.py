# https://adventofcode.com/2023/day/4

from collections import defaultdict

from ...base import StrSplitSolution, answer


def num_matching_numbers(line: str) -> int:
    _, rest = line.split(":")
    winners, nums = rest.split("|")
    # Count only the numbers in common between both lists
    return len(set(winners.split()) & set(nums.split()))


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 4.
    """
    _year = 2023
    _day = 4

    @answer(23847)
    def part_1(self) -> int:
        return sum(
            int(2 ** (num_matching_numbers(line) - 1))
            for line in self.input
        )

    @answer(8570000)
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
