# https://adventofcode.com/2024/day/20

from collections.abc import Iterator

from ...base import StrSplitSolution, answer
from ...utils.grids import (
    add_points, GridPoint, neighbors, parse_grid, taxicab_distance,
)


def points_within_radius(
        center: GridPoint,
        radius: int,
) -> Iterator[GridPoint]:
    """
    Yield all points within a given radius of the center point (by
    taxicab distance).
    """
    for dx in range(-radius, radius + 1):
        max_dy = radius - abs(dx)
        for dy in range(-max_dy, max_dy + 1):
            yield add_points(center, (dx, dy))


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 20.
    """
    _year = 2024
    _day = 20

    def _solve(self, cheat_length: int) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        start = next(k for k, v in grid.items() if v == "S")
        end = next(k for k, v in grid.items() if v == "E")

        # Find the distances of all tiles from the start
        # NOTE This assumes there is only one path to the end.
        distances = {start: 0}
        loc = start
        while loc != end:
            # Move to the next neighbor that's in the grid and that
            # hasn't yet been visited
            new_loc = next(
                n for n in neighbors(loc, num_directions=4)
                if n in grid and n not in distances
            )
            # We've moved forward by one tile
            distances[new_loc] = distances[loc] + 1
            loc = new_loc

        # A potential cheat is a cheat within the allowed length
        potential_cheats = (
            (a, b)
            for a in distances.keys()
            for b in distances.keys() & points_within_radius(a, cheat_length)
        )
        # A good cheat is a cheat that saves at least 100 picoseconds
        # over travelling on the path normally
        num_good_cheats = sum(
            1
            for a, b in potential_cheats
            if taxicab_distance(a, b) <= distances[b] - distances[a] - 100
        )
        return num_good_cheats

    @answer(1530)
    def part_1(self) -> int:
        return self._solve(cheat_length=2)

    @answer(1033983)
    def part_2(self) -> int:
        return self._solve(cheat_length=20)
