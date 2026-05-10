# https://adventofcode.com/2024/day/8

from collections import defaultdict
from itertools import permutations

from ...base import StrSplitSolution, answer
from ...utils.grids import (
    Grid, GridPoint, add_points, parse_grid, subtract_points,
)


def find_antennas(grid: Grid[str]) -> dict[str, list[GridPoint]]:
    antennas: dict[str, list[GridPoint]] = defaultdict(list)
    for point, char in grid.items():
        if char != ".":
            antennas[char].append(point)
    return antennas


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 8.
    """
    _year = 2024
    _day = 8

    @answer((400, 1280))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        antennas = find_antennas(grid)

        weak_antinodes: set[GridPoint] = set()
        strong_antinodes: set[GridPoint] = set()
        for locations in antennas.values():
            for a, b in permutations(locations, 2):
                distance = subtract_points(b, a)

                # The weak antinode is just past B
                antinode = add_points(b, distance)
                if antinode in grid:
                    weak_antinodes.add(antinode)

                # The strong antinodes are B and the locations past it
                antinode = b
                while antinode in grid:
                    strong_antinodes.add(antinode)
                    antinode = add_points(antinode, distance)

        return len(weak_antinodes), len(strong_antinodes)
