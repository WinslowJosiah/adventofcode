from collections.abc import Iterable
from typing import TypeAlias


Location: TypeAlias = tuple[int, int]


def parse_grid(lines: Iterable[str]) -> dict[Location, int]:
    """
    Parse lines of text into a grid.
    """
    grid: dict[Location, int] = {}
    for r, row in enumerate(lines):
        for c, char in enumerate(row):
            grid[(r, c)] = int(char)
    return grid


def aoc2024_day10_part1(lines: Iterable[str]) -> int:
    grid = parse_grid(lines)

    def get_trailhead_score(location: Location) -> int:
        """
        Get the score of this trailhead, where the score is the number
        of unique 9-height locations reachable from this 0-height
        location.

        If this location doesn't have a height of 0, this can't be a
        trailhead, and it is given a default score of 0.
        """
        max_height_locations: set[tuple[int, int]] = set()
        def walk(r: int, c: int, height: int = 0):
            # Stop walking if this location is outside the grid, or if
            # the height doesn't match
            if grid.get((r, c), None) != height:
                return
            # If the height here is 9
            if height >= 9:
                # Mark this location has visited and stop walking
                max_height_locations.add((r, c))
                return

            # Try walking from all directions
            walk(r + 1, c, height + 1)
            walk(r - 1, c, height + 1)
            walk(r, c + 1, height + 1)
            walk(r, c - 1, height + 1)

        # Start walking from this location
        walk(*location)
        return len(max_height_locations)

    return sum(map(get_trailhead_score, grid))


def aoc2024_day10_part2(lines: Iterable[str]) -> int:
    grid = parse_grid(lines)

    def get_trailhead_score(location: Location) -> int:
        """
        Get the score of this trailhead, where the score is the number
        of unique trails that reach a 9-height location from this
        0-height location.

        If this location doesn't have a height of 0, this can't be a
        trailhead, and it is given a default score of 0.
        """
        score = 0
        def walk(r: int, c: int, height: int = 0):
            nonlocal score

            # Stop walking if this location is outside the grid, or if
            # the height doesn't match
            if grid.get((r, c), None) != height:
                return
            # If the height here is 9
            if height >= 9:
                # Add to the trailhead score and stop walking
                score += 1
                return

            # Try walking from all directions
            walk(r + 1, c, height + 1)
            walk(r - 1, c, height + 1)
            walk(r, c + 1, height + 1)
            walk(r, c - 1, height + 1)

        # Start walking from this location
        walk(*location)
        return score

    return sum(map(get_trailhead_score, grid))


parts = (aoc2024_day10_part1, aoc2024_day10_part2)
