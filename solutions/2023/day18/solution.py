# https://adventofcode.com/2023/day/18

from collections.abc import Callable

from ...base import StrSplitSolution, answer
from ...utils.grids import Direction, GridPoint, add_points, interior_area


DIRECTIONS = {
    "U": Direction.UP.offset,
    "R": Direction.RIGHT.offset,
    "D": Direction.DOWN.offset,
    "L": Direction.LEFT.offset,
}
OFFSETS = list(DIRECTIONS.values())


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 18.
    """
    _year = 2023
    _day = 18

    def _solve(
            self,
            get_instruction: Callable[[str], tuple[GridPoint, int]],
    ) -> int:
        points: list[GridPoint] = [(0, 0)]
        num_boundary_points = 0
        for line in self.input:
            offset, distance = get_instruction(line)
            scaled_offset = offset[0] * distance, offset[1] * distance
            points.append(add_points(scaled_offset, points[-1]))
            num_boundary_points += distance

        area = interior_area(points)
        # NOTE Pick's theorem relates the area, number of interior grid
        # points, and number of boundary grid points of a simple lattice
        # polygon. This formula follows from simple algebra.
        num_interior_points = int(area - num_boundary_points / 2 + 1)
        return num_interior_points + num_boundary_points

    @answer(49061)
    def part_1(self) -> int:
        def parse_line(line: str) -> tuple[GridPoint, int]:
            direction, distance_str, _ = line.split()
            return DIRECTIONS[direction], int(distance_str)
        return self._solve(parse_line)

    @answer(92556825427032)
    def part_2(self) -> int:
        def parse_line(line: str) -> tuple[GridPoint, int]:
            _, _, hex_str = line.split()
            offset = OFFSETS[int(hex_str[-2])]
            distance = int(hex_str[2:-2], base=16)
            return offset, distance
        return self._solve(parse_line)
