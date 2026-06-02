# https://adventofcode.com/2024/day/12

from collections.abc import Iterator

from ...base import StrSplitSolution, answer
from ...utils.grids import Grid, GridPoint, neighbors, offsets, parse_grid


def matching_neighbors(
        grid: Grid[str],
        point: GridPoint,
) -> Iterator[GridPoint]:
    for n in neighbors(point, num_directions=4):
        if grid.get(n) == grid[point]:
            yield n


def iter_regions(grid: Grid[str]) -> Iterator[set[GridPoint]]:
    seen: set[GridPoint] = set()
    for point in grid:
        if point in seen:
            continue

        region: set[GridPoint] = set()
        # Regions will be determined using flood fill
        queue = [point]
        while queue:
            current = queue.pop()
            if current in region:
                continue

            region.add(current)
            queue.extend(matching_neighbors(grid, current))

        seen |= region
        yield region


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 12.
    """
    _year = 2024
    _day = 12

    @answer((1446042, 902742))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)

        perimeter_price, side_price = 0, 0
        for region in iter_regions(grid):
            # NOTE Each region has exactly as many sides as corners.
            # Thus, we can simply count the corners to count the sides.
            perimeter, num_corners = 0, 0
            for point in region:
                # Count all non-matching neighbors of this point
                perimeter += 4 - len(list(matching_neighbors(grid, point)))

                row, col = point
                # For each possible offset of a corner
                for dr, dc in offsets(num_directions=4, diagonals=True):
                    has_row_neighbor = (row + dr, col) in region
                    has_col_neighbor = (row, col + dc) in region
                    has_diagonal_neighbor = (row + dr, col + dc) in region

                    # Is this an outer corner?
                    if not has_row_neighbor and not has_col_neighbor:
                        num_corners += 1
                    # Is this an inner corner?
                    if (
                        has_row_neighbor and has_col_neighbor
                        and not has_diagonal_neighbor
                    ):
                        num_corners += 1

            perimeter_price += perimeter * len(region)
            side_price += num_corners * len(region)

        return perimeter_price, side_price
