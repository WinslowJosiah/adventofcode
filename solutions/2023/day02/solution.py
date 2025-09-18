# https://adventofcode.com/2023/day/2

from collections import defaultdict
from math import prod
import re

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 2.
    """
    _year = 2023
    _day = 2

    @answer(2239)
    def part_1(self) -> int:
        BAG = {"red": 12, "green": 13, "blue": 14}

        total = 0
        for game_id, game in enumerate(self.input, start=1):
            _, cubes = game.split(": ")

            # This game is possible if all cube counts are within the
            # given cube counts of the bag
            if all(
                int(count) <= BAG[color]
                for count, color in re.findall(r"(\d+) (\w+)", cubes)
            ):
                total += game_id

        return total

    @answer(83435)
    def part_2(self) -> int:
        total = 0
        for game in self.input:
            _, cubes = game.split(": ")

            # The minimum amount of each cube is however many of that
            # cube were drawn in the biggest draw
            min_bag: dict[str, int] = defaultdict(int)
            for count, color in re.findall(r"(\d+) (\w+)", cubes):
                min_bag[color] = max(min_bag[color], int(count))

            total += prod(min_bag.values())

        return total
