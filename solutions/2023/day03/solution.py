# https://adventofcode.com/2023/day/3

from collections import defaultdict
from operator import mul
import re

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 3.
    """
    _year = 2023
    _day = 3

    def _pad_input(self) -> list[str]:
        """
        Pad the input grid with two rows of dots.
        """
        grid_width = len(self.input[0])
        return ["." * grid_width, *self.input, "." * grid_width]

    @answer(556367)
    def part_1(self) -> int:
        grid = self._pad_input()
        RE_SYMBOL = re.compile(r"[^\d.]")

        total = 0
        for row_index, row in enumerate(grid):
            for number in re.finditer(r"\d+", row):
                start, end = number.span()
                part_num = int(number.group())

                # Check for symbols in previous, current, and next rows
                if any(
                    RE_SYMBOL.search(
                        grid[symbol_row_index], start - 1, end + 1,
                    )
                    for symbol_row_index in range(row_index - 1, row_index + 2)
                ):
                    total += part_num

        return total

    @answer(89471771)
    def part_2(self) -> int:
        grid = self._pad_input()
        RE_GEAR = re.compile(r"\*")

        gears: dict[tuple[int, int], list[int]] = defaultdict(list)
        for row_index, row in enumerate(grid):
            for number in re.finditer(r"\d+", row):
                start, end = number.span()
                part_num = int(number.group())

                # Find gears in previous, current, and next rows
                for gear_row_index in range(row_index - 1, row_index + 2):
                    for gear_match in RE_GEAR.finditer(
                        grid[gear_row_index], start - 1, end + 1,
                    ):
                        gear_pos = gear_row_index, gear_match.start()
                        gears[gear_pos].append(part_num)

        return sum(mul(*nums) for nums in gears.values() if len(nums) == 2)
