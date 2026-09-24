# https://adventofcode.com/2024/day/19

from functools import cache

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 19.
    """
    _year = 2024
    _day = 19

    separator = "\n\n"

    @answer((315, 625108891232249))
    def solve(self) -> tuple[int, int]:
        raw_towels, raw_designs = self.input
        towels = raw_towels.split(", ")
        designs = raw_designs.splitlines()

        @cache
        def count_arrangements(design: str) -> int:
            # An empty design (with no stripes) can be made in one way
            # (by using no towels)
            if not design:
                return 1
            # For each towel that could go first, count the possible
            # towel arrangements for the rest of the design
            return sum(
                count_arrangements(design.removeprefix(towel))
                for towel in towels
                if design.startswith(towel)
            )

        arrangements = [count_arrangements(design) for design in designs]
        # Part 1 counts designs with a nonzero number of arrangements;
        # Part 2 counts all arrangements for all designs
        return sum(map(bool, arrangements)), sum(arrangements)
