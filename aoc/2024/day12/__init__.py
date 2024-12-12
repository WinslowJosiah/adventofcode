from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeAlias


Vector: TypeAlias = tuple[int, int]
Grid: TypeAlias = dict[Vector, str]
Region: TypeAlias = set[Vector]
OFFSETS: tuple[Vector, ...] = ((0, -1), (0, 1), (-1, 0), (1, 0))


def parse_grid(lines: Iterable[str]) -> Grid:
    """
    Parse lines of text into a grid.
    """
    grid: Grid = {}
    for r, row in enumerate(lines):
        for c, char in enumerate(row):
            grid[(r, c)] = char
    return grid


def iter_regions(grid: Grid) -> Iterator[Region]:
    """
    Iterate through each region of the grid.
    """
    # We shall identify regions with a flood-fill
    filled: set[Vector] = set()

    for pos, plant in grid.items():
        # Skip if this position was already flood-filled
        # NOTE Because we skip all positions in a region after the first
        # one found, we can treat this loop as looping through each
        # region once.
        if pos in filled:
            continue

        region: Region = set()
        # Initialize the flood-fill queue
        plots = deque([pos])
        # While there are plots left to process
        while plots:
            plot = plots.popleft()
            # Skip if this plot was already flood-filled
            if plot in filled:
                continue
            # Skip if this plot doesn't match this region's plant
            if grid.get(plot, "") != plant:
                continue

            # This plot has been flood-filled and is part of this region
            filled.add(plot)
            region.add(plot)
            # Add each neighboring plot to the flood-fill queue
            pr, pc = plot
            for dr, dc in OFFSETS:
                plots.append((pr + dr, pc + dc))

        yield region


def get_perimeter(region: Region) -> int:
    """
    Calculate the perimeter of this region.
    """
    perimeter = 0
    for dr, dc in OFFSETS:
        for pr, pc in region:
            # If the adjacent plot isn't in the region
            if (pr + dr, pc + dc) not in region:
                # That side counts toward the perimeter
                perimeter += 1
    return perimeter


def get_side_count(region: Region) -> int:
    """
    Calculate the side-count of this region.
    """
    side_count = 0
    for dr, dc in OFFSETS:
        analyzed: set[Vector] = set()
        for plot in region:
            # Skip if we've analyzed this plot already
            if plot in analyzed:
                continue
            pr, pc = plot
            # Skip if the adjacent plot is in the region
            if (pr + dr, pc + dc) in region:
                continue

            # If we're here, the adjacent side counts toward the
            # side-count
            side_count += 1
            # We will mark this entire side as analyzed
            for scan_delta in (-1, 1):
                r, c = plot
                while (r, c) in region and (r + dr, c + dc) not in region:
                    analyzed.add((r, c))
                    # Scan perpendicular to the offset direction
                    r += dc * scan_delta
                    c += dr * scan_delta

    return side_count


def aoc2024_day12_part1(lines: Iterable[str]) -> int:
    grid = parse_grid(lines)

    price = 0
    for region in iter_regions(grid):
        area = len(region)
        perimeter = get_perimeter(region)
        price += area * perimeter
    return price


def aoc2024_day12_part2(lines: Iterable[str]) -> int:
    grid = parse_grid(lines)

    price = 0
    for region in iter_regions(grid):
        area = len(region)
        side_count = get_side_count(region)
        price += area * side_count
    return price


parts = (aoc2024_day12_part1, aoc2024_day12_part2)
