# https://adventofcode.com/2023/day/1

import re
from typing import cast

from ...base import StrSplitSolution, answer


DIGITS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def get_calibration(line: str, include_spelled: bool = False) -> int:
    VALID_DIGITS = list(DIGITS.values())
    if include_spelled:
        VALID_DIGITS.extend(DIGITS.keys())
    # NOTE The regex will look something like /(?=(a|b|c|d))/, which
    # uses positive lookahead to find any point in the line immediately
    # followed by a valid digit (and captures that digit).
    DIGIT_REGEX = rf"(?=({"|".join(VALID_DIGITS)}))"

    digits = [
        DIGITS.get(match, cast(str, match))
        for match in re.findall(DIGIT_REGEX, line)
    ]

    # HACK The test cases have lines without literal digits, which would
    # make them fail on Part 1 without this failsafe.
    if not digits:
        return 0
    return int(digits[0] + digits[-1])


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 1.
    """
    _year = 2023
    _day = 1

    @answer(52974)
    def part_1(self) -> int:
        return sum(
            get_calibration(line, include_spelled=False) for line in self.input
        )

    @answer(53340)
    def part_2(self) -> int:
        return sum(
            get_calibration(line, include_spelled=True) for line in self.input
        )
