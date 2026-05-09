# https://adventofcode.com/2024/day/6

from ...base import StrSplitSolution, answer, slow
from ...utils.grids import Grid, Direction, Position, parse_grid


def track_guard(grid: Grid[str], guard: Position) -> list[Position] | None:
    # HACK This dict is being used as an "ordered set", so to speak. It
    # stores the positions in order (with values of None), and we can
    # quickly check whether it contains a certain position.
    path: dict[Position, None] = {}

    while guard.point in grid:
        if guard in path:
            return None
        path[guard] = None

        if grid.get(guard.next_point) == "#":
            guard = guard.rotate("CW")
        else:
            guard = guard.step()

    return list(path)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 6.
    """
    _year = 2024
    _day = 6

    @answer((4890, 1995))
    @slow
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        guard = Position(
            point=next(k for k, v in grid.items() if v == "^"),
            facing=Direction.UP,
        )
        path = track_guard(grid, guard)
        assert path is not None
        points_seen = {p.point for p in path}

        num_obstacle_placements = 0
        for obstacle_point in points_seen:
            # An obstacle can only be placed on an empty tile
            if grid[obstacle_point] != ".":
                continue

            # Try placing an obstacle here
            grid[obstacle_point] = "#"
            # NOTE Because the guard's path will be identical up to the
            # obstacle, we can start the guard directly before it.
            blocked_guard = next(
                p for p in path if p.next_point == obstacle_point
            )
            blocked_path = track_guard(grid, blocked_guard)
            # If the guard got stuck in a loop, tally this placement
            if blocked_path is None:
                num_obstacle_placements += 1
            # Un-place the obstacle
            grid[obstacle_point] = "."

        return len(points_seen), num_obstacle_placements
