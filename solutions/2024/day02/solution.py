# https://adventofcode.com/2024/day/2

from collections.abc import Sequence
from itertools import combinations, pairwise

from ...base import StrSplitSolution, answer


def parse_report(line: str) -> list[int]:
    return [int(level) for level in line.split()]


def is_safe_increasing(report: Sequence[int]) -> bool:
    return all(1 <= b - a <= 3 for a, b in pairwise(report))


def is_safe(report: Sequence[int]) -> bool:
    return is_safe_increasing(report) or is_safe_increasing(report[::-1])


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 2.
    """
    _year = 2024
    _day = 2

    @answer(624)
    def part_1(self) -> int:
        return sum(is_safe(parse_report(line)) for line in self.input)

    @answer(658)
    def part_2(self) -> int:
        reports = [parse_report(line) for line in self.input]
        return sum(
            # NOTE We don't need to check whether the original report is
            # safe; using the "Problem Dampener" on a safe report
            # doesn't change its safeness.
            any(
                is_safe(levels)
                # NOTE Each returned combination will be in the same
                # order, but with one item removed.
                for levels in combinations(report, len(report) - 1)
            )
            for report in reports
        )
