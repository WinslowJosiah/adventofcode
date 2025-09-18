# https://adventofcode.com/2023/day/11

from itertools import combinations

from ...base import StrSplitSolution, answer
from ...utils.grids import GridPoint, parse_grid, taxicab_distance


def get_expanded_values(
        points: list[GridPoint],
        dim: int,
        multiplier: int,
) -> list[int]:
    filled_lines = {p[dim] for p in points}
    max_coordinate = max(filled_lines)

    expanded_values: list[int] = []
    offset = 0
    for i in range(max_coordinate + 1):
        expanded_values.append(i + offset)
        if i not in filled_lines:
            offset += multiplier - 1

    return expanded_values


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 11.
    """
    _year = 2023
    _day = 11

    def _solve(self, multiplier: int) -> int:
        points = list(parse_grid(self.input, ignore_chars=".").keys())

        expanded_rows = get_expanded_values(points, 0, multiplier)
        expanded_columns = get_expanded_values(points, 1, multiplier)
        expanded_points = [
            (expanded_rows[row], expanded_columns[col])
            for row, col in points
        ]

        return sum(
            taxicab_distance(a, b)
            for a, b in combinations(expanded_points, 2)
        )

    @answer(9608724)
    def part_1(self) -> int:
        return self._solve(multiplier=2)

    @answer(904633799472)
    def part_2(self) -> int:
        return self._solve(multiplier=1_000_000)
