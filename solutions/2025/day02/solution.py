# https://adventofcode.com/2025/day/2

from collections.abc import Iterator
import re

from ...base import StrSplitSolution, answer


def iter_ranges(raw_ranges: list[str]) -> Iterator[int]:
    for raw_range in raw_ranges:
        start, stop = map(int, raw_range.split("-"))
        # NOTE The stop of the input range is inclusive.
        yield from range(start, stop + 1)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 2.
    """
    _year = 2025
    _day = 2

    separator = ","

    def _solve(self, at_least_twice: bool) -> int:
        pattern = re.compile(r"^(.+)\1+$" if at_least_twice else r"^(.+)\1$")
        return sum(
            n
            for n in iter_ranges(self.input)
            if pattern.match(str(n))
        )

    @answer(28146997880)
    def part_1(self) -> int:
        return self._solve(at_least_twice=False)

    @answer(40028128307)
    def part_2(self) -> int:
        return self._solve(at_least_twice=True)
