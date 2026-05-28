# https://adventofcode.com/2024/day/10

from ...base import StrSplitSolution, answer
from ...utils.grids import neighbors, parse_grid, Grid, GridPoint


def get_trailhead_ends(
        grid: Grid[int],
        trailhead: GridPoint,
) -> list[GridPoint]:
    queue = [trailhead]
    ends: list[GridPoint] = []
    while queue:
        point = queue.pop()
        # If our point has height 9, it is the end of a trail
        if (height := grid[point]) == 9:
            ends.append(point)
            continue
        # Continue walking along points that are exactly 1 higher
        queue.extend(
            n for n in neighbors(point, num_directions=4)
            if grid.get(n) == height + 1
        )
    return ends


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 10.
    """
    _year = 2024
    _day = 10

    @answer((611, 1380))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, int, ignore_chars=".")

        total_scores, total_ratings = 0, 0
        for point, height in grid.items():
            # Only count ends from trailheads, i.e. points with height 0
            if height != 0:
                continue
            ends = get_trailhead_ends(grid, point)
            total_scores += len(set(ends))
            total_ratings += len(ends)

        return total_scores, total_ratings
