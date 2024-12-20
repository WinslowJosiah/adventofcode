from collections import defaultdict
from collections.abc import Iterable
from typing import TypeAlias


Vector: TypeAlias = complex
Grid: TypeAlias = defaultdict[Vector, str]
OFFSETS: tuple[Vector, ...] = (1 + 0j, -1 + 0j, 1j, -1j)


def parse_input(lines: Iterable[str]) -> tuple[Grid, Vector, Vector]:
    """
    Parse the input, and return a grid, a starting position, and an
    ending position.
    """
    grid: Grid = defaultdict(lambda: "#")
    start_pos, end_pos = None, None
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            pos = x + y * 1j
            if char == "S":
                start_pos = pos
            elif char == "E":
                end_pos = pos
            grid[pos] = char
    assert start_pos is not None and end_pos is not None
    return grid, start_pos, end_pos


def count_good_cheats(
        grid: Grid,
        start_pos: Vector,
        end_pos: Vector,
        cheat_length: int,
) -> int:
    """
    Count the number of "cheats" that can be done in the grid that save
    100 picoseconds or more.
    """
    # Start by finding the one path from the start to the end
    pos = start_pos
    # We will record the position along the path at each point
    path: dict[Vector, int] = {start_pos: 0}
    # Until we reach the end
    while pos != end_pos:
        for offset in OFFSETS:
            next_pos = pos + offset
            # Don't move into a wall...
            if grid[next_pos] == "#":
                continue
            # ...or revisit a previously visited tile
            if next_pos in path:
                continue

            # This is the next position along the path
            # NOTE This assumes there are no branches along the path.
            pos = next_pos
            break
        else:
            raise RuntimeError("no path forward exists")

        # Record this position along the path
        path[pos] = len(path)

    good_cheats = 0
    # For every point along the path
    for pos, move in path.items():
        # For each valid cheat that can be done here
        # NOTE For each valid cheat, the sum of the absolute changes of
        # X and Y is at most the allowed length of the cheat.
        dx_limit = cheat_length
        for dx in range(-dx_limit, dx_limit + 1):
            dy_limit = cheat_length - abs(dx)
            for dy in range(-dy_limit, dy_limit + 1):
                cheat = dx + dy * 1j
                cheat_pos = pos + cheat

                # Don't do this cheat if it would move us into a wall...
                if grid[cheat_pos] == "#":
                    continue
                cheat_move = path.get(cheat_pos, None)
                if (
                    # ...or if it would move us outside the grid...
                    cheat_move is None
                    # ...or if it wouldn't save enough time
                    or cheat_move - (move + abs(dx) + abs(dy)) < 100
                ):
                    continue

                # This is a good cheat
                good_cheats += 1

    return good_cheats


def aoc2024_day20_part1(lines: Iterable[str]) -> int:
    grid, start_pos, end_pos = parse_input(lines)
    return count_good_cheats(grid, start_pos, end_pos, cheat_length=2)


def aoc2024_day20_part2(lines: Iterable[str]) -> int:
    grid, start_pos, end_pos = parse_input(lines)
    return count_good_cheats(grid, start_pos, end_pos, cheat_length=20)


parts = (aoc2024_day20_part1, aoc2024_day20_part2)
