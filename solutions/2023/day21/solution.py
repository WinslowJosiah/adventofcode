# https://adventofcode.com/2023/day/21

from collections import deque

from ...base import StrSplitSolution, answer
from ...utils.grids import Grid, GridPoint, neighbors, parse_grid


def num_paths(grid: Grid[str], grid_size: int, path_length: int) -> int:
    start = next(k for k, v in grid.items() if v == "S")
    visited: dict[GridPoint, int] = {}
    queue: deque[tuple[int, GridPoint]] = deque([(0, start)])
    while queue:
        distance, point = queue.popleft()
        if point in visited or distance > path_length:
            continue
        visited[point] = distance

        for n in neighbors(point, num_directions=4):
            n_wrapped = n[0] % grid_size, n[1] % grid_size
            if n_wrapped in grid:
                queue.append((distance + 1, n))

    # NOTE If a point's distance has the same parity as the path length,
    # it can be reached through some amount of doubling back.
    return sum(v % 2 == path_length % 2 for v in visited.values())


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 21.
    """
    _year = 2023
    _day = 21

    @answer((3689, 610158187362102))
    def solve(self) -> tuple[int, int]:
        assert len(self.input) == len(self.input[0]), "not a square grid"
        grid_size = len(self.input)
        grid = parse_grid(self.input, ignore_chars="#")

        num_short_paths = num_paths(grid, grid_size, 64)

        # NOTE The middle row and column happen to be blank, so taking a
        # straight path should bring us directly onto the edge of one of
        # the infinitely-repeating garden plots. n is the maximum number
        # of garden plots outward that we can traverse.
        NUM_STEPS = 26501365
        n, remainder = divmod(NUM_STEPS - grid_size // 2, grid_size)
        assert remainder == 0, "radius isn't whole number of garden plots"

        # HACK Traversing outward by whole numbers of garden plots leads
        # to results that happen to follow a quadratic curve. Using some
        # algebra, we can derive the coefficients of that curve from the
        # results of traversing 0, 1, and 2 garden plots. We can then
        # directly calculate the result of traversing n garden plots.
        f0, f1, f2 = (
            num_paths(grid, grid_size, plots * grid_size + grid_size // 2)
            for plots in range(3)
        )
        a = (f2 - 2 * f1 + f0) / 2
        b = f1 - f0 - a
        c = f0
        num_long_paths = round(a * n ** 2 + b * n + c)

        return num_short_paths, num_long_paths
