# https://adventofcode.com/2023/day/6

from math import ceil, floor, prod, sqrt

from ...base import StrSplitSolution, answer


def num_race_wins(time: int, distance: int) -> int:
    # NOTE The distance the boat travels is b * (t - b), where b is the
    # time spent holding the button, and t is the total race time; we
    # want the amount of b values where this distance is greater than
    # the record. To do this, I use some carefully handled algebra.
    halfway = time / 2
    offset = sqrt(halfway * halfway - distance)
    lower_root = floor(halfway - offset)
    upper_root = ceil(halfway + offset)
    # NOTE This is the length of the range, excluding the two endpoints.
    return upper_root - lower_root - 1


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 6.
    """
    _year = 2023
    _day = 6

    @answer(303600)
    def part_1(self) -> int:
        times, distances = [
            list(map(int, line.split()[1:]))
            for line in self.input
        ]
        return prod(
            num_race_wins(time, distance)
            for time, distance in zip(times, distances)
        )

    @answer(23654842)
    def part_2(self) -> int:
        time, distance = [
            int("".join(line.split()[1:]))
            for line in self.input
        ]
        return num_race_wins(time, distance)
