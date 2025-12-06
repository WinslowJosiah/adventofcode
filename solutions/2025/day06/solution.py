# https://adventofcode.com/2025/day/6

from collections.abc import Callable, Iterable, Sequence
from functools import reduce
from itertools import groupby
from operator import add, mul

from ...base import StrSplitSolution, answer


OPERATORS: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "*": mul,
}


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 6.
    """
    _year = 2025
    _day = 6

    def _solve(
            self,
            number_groups: Sequence[Iterable[int]],
            symbols: Sequence[str],
    ) -> int:
        return sum(
            reduce(OPERATORS[symbol], numbers)
            for numbers, symbol in zip(number_groups, symbols)
        )

    @answer(4693159084994)
    def part_1(self) -> int:
        *raw_numbers, raw_symbols = self.input

        symbols = raw_symbols.split()
        rows = [map(int, row.split()) for row in raw_numbers]
        number_groups: list[tuple[int, ...]] = list(zip(*rows))

        return self._solve(number_groups, symbols)

    @answer(11643736116335)
    def part_2(self) -> int:
        *raw_numbers, raw_symbols = self.input

        def is_all_spaces(column: Sequence[str]) -> bool:
            return all(char == " " for char in column)

        symbols = raw_symbols.split()[::-1]
        columns = list(zip(*raw_numbers))[::-1]
        number_groups = [
            [int("".join(column)) for column in group]
            for is_separator, group in groupby(columns, key=is_all_spaces)
            if not is_separator
        ]

        return self._solve(number_groups, symbols)
