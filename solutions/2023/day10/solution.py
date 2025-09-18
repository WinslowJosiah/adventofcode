# https://adventofcode.com/2023/day/10

from ...base import StrSplitSolution, answer
from ...utils.grids import (
    Direction, Grid, GridPoint, add_points, interior_area, neighbors,
    parse_grid,
)


PIPES = {
    "|": (Direction.UP, Direction.DOWN),
    "-": (Direction.RIGHT, Direction.LEFT),
    "L": (Direction.UP, Direction.RIGHT),
    "J": (Direction.UP, Direction.LEFT),
    "7": (Direction.DOWN, Direction.LEFT),
    "F": (Direction.RIGHT, Direction.DOWN),
}


def possible_moves(current: GridPoint, ch: str) -> tuple[GridPoint, GridPoint]:
    result = tuple(add_points(current, d.offset) for d in PIPES[ch])
    assert len(result) == 2
    return result


def get_moves_from_start(grid: Grid[str], start: GridPoint) -> list[GridPoint]:
    moves: list[GridPoint] = []
    for neighbor in neighbors(start, num_directions=4):
        if neighbor not in grid:
            continue
        if start in possible_moves(neighbor, grid[neighbor]):
            moves.append(neighbor)
    assert len(moves) == 2, "didn't find two moves possible from start"
    return moves


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 10.
    """
    _year = 2023
    _day = 10

    @answer((7173, 291))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, ignore_chars=".")
        start = next(k for k, v in grid.items() if v == "S")

        points = [start]
        current = get_moves_from_start(grid, start)[0]
        while current != start:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])
            current = a if b == last else b

        # The farthest point from the start is the halfway point of the
        # loop
        farthest_loop_distance = len(points) // 2

        area = interior_area(points)
        # NOTE Pick's theorem relates the area, number of interior grid
        # points, and number of boundary grid points of a simple lattice
        # polygon. This formula follows from simple algebra.
        num_interior_points = int(area - len(points) / 2 + 1)

        return farthest_loop_distance, num_interior_points
