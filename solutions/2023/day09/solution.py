# https://adventofcode.com/2023/day/9

from itertools import pairwise

from ...base import StrSplitSolution, answer


def extrapolate(history: list[int]) -> int:
    if not any(history):
        return 0
    diffs = [b - a for a, b in pairwise(history)]
    return history[-1] + extrapolate(diffs)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 9.
    """
    _year = 2023
    _day = 9

    def _solve(self, reverse: bool) -> int:
        histories = [list(map(int, line.split())) for line in self.input]
        return sum(extrapolate(h[::-1] if reverse else h) for h in histories)

    @answer(2105961943)
    def part_1(self) -> int:
        return self._solve(reverse=False)

    @answer(1019)
    def part_2(self) -> int:
        return self._solve(reverse=True)
