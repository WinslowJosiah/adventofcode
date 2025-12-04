# https://adventofcode.com/2025/day/4

from ...base import StrSplitSolution, answer
from ...utils.grids import GridPoint, neighbors, parse_grid


def is_accessible(rolls: set[GridPoint], point: GridPoint) -> bool:
    num_neighbors = sum(
        1
        for n in neighbors(point, num_directions=8)
        if n in rolls
    )
    return num_neighbors < 4


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 4.
    """
    _year = 2025
    _day = 4

    @answer(1587)
    def part_1(self) -> int:
        rolls = set(parse_grid(self.input, ignore_chars=".").keys())
        return sum(is_accessible(rolls, point) for point in rolls)

    @answer(8946)
    def part_2(self) -> int:
        rolls = set(parse_grid(self.input, ignore_chars=".").keys())

        total = 0
        while True:
            accessible_points = {
                point
                for point in rolls
                if is_accessible(rolls, point)
            }
            # Loop until no more rolls are accessible
            if not accessible_points:
                break

            total += len(accessible_points)
            rolls -= accessible_points

        return total
