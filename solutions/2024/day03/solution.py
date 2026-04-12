# https://adventofcode.com/2024/day/3

import re

from ...base import TextSolution, answer


def get_mul_total(program: str) -> int:
    """
    Get the sum of the `mul()` commands in a program. `do()` and
    `don't()` commands are ignored; only the `mul()` commands are done.
    """
    return sum(
        int(a) * int(b)
        for a, b in re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", program)
    )


class Solution(TextSolution):
    """
    Solution for Advent of Code 2024 Day 3.
    """
    _year = 2024
    _day = 3

    @answer(167650499)
    def part_1(self) -> int:
        return get_mul_total(self.input)

    @answer(95846796)
    def part_2(self) -> int:
        segments_to_do = re.findall(
            r"""
                (?:^|do\(\))     # start of input, or do()
                (.*?)            # whatever's in between (lazily)
                (?:don't\(\)|$)  # don't(), or end of input
            """,
            self.input,
            flags=re.DOTALL | re.VERBOSE,
        )
        return sum(get_mul_total(segment) for segment in segments_to_do)
