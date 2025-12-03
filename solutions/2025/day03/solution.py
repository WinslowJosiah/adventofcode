# https://adventofcode.com/2025/day/3

from ...base import StrSplitSolution, answer


def max_joltage(bank: str, batteries: int) -> str:
    # No possible joltage if there aren't enough batteries for it
    assert len(bank) >= batteries, "no possible max joltage"
    # The max joltage with a single battery is the bank's highest digit
    if batteries == 1:
        return max(bank)

    # Find highest first digit (leaving enough space for the rest of the
    # batteries)
    first_digit = max(bank[: -(batteries - 1)])
    # Combine that digit with the max joltage for the rest of the bank
    i = bank.index(first_digit)
    return first_digit + max_joltage(bank[i + 1 :], batteries - 1)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 3.
    """
    _year = 2025
    _day = 3

    @answer(17092)
    def part_1(self) -> int:
        return sum(int(max_joltage(line, batteries=2)) for line in self.input)

    @answer(170147128753455)
    def part_2(self) -> int:
        return sum(int(max_joltage(line, batteries=12)) for line in self.input)
