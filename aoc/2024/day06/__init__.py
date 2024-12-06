from collections.abc import Iterable
from typing import TypeAlias


Vector: TypeAlias = tuple[int, int]
Grid: TypeAlias = dict[Vector, str]


def parse_grid(lines: Iterable[str]) -> tuple[Grid, Vector | None]:
    """
    Parse a series of lines into a grid and an initial guard position.
    """
    grid: Grid = {}
    guard = None
    for r, row in enumerate(lines):
        for c, char in enumerate(row):
            grid[(r, c)] = char
            if char == "^":
                guard = (r, c)
    return grid, guard


def walk_guard(
        grid: Grid,
        guard: Vector,
        direction: Vector,
        obstacle: Vector | None = None,
) -> tuple[list[tuple[Vector, Vector]], bool]:
    """
    Walk the guard through the grid, until she either steps outside the
    grid or loops. Returns the path the guard takes, and whether or not
    the path loops.
    """
    guard_r, guard_c = guard
    direction_r, direction_c = direction

    # For each tile on the guard's path, we will store its location and
    # the direction the guard is facing
    path: list[tuple[Vector, Vector]] = []
    # NOTE Although we want to return the path in order, using a set
    # speeds up the process of checking for loops.
    path_set: set[tuple[Vector, Vector]] = set()

    while True:
        path_item = (
            (guard_r, guard_c),
            (direction_r, direction_c),
        )
        # If we've visited this tile from this direction before
        if path_item in path_set:
            # We are in a loop
            return path, True
        # Mark this tile as visited from this direction
        path.append(path_item)
        path_set.add(path_item)

        guard_next = (guard_r + direction_r, guard_c + direction_c)
        # If our next step is outside the grid
        if guard_next not in grid:
            # We have finished without a loop
            return path, False

        # If there is something in front of us
        if obstacle == guard_next or grid[guard_next] == "#":
            # Turn 90 degrees
            direction_r, direction_c = direction_c, -direction_r
        else:
            # Otherwise, step forward
            guard_r, guard_c = guard_next


def aoc2024_day06_part1(lines: Iterable[str]) -> int:
    grid, guard = parse_grid(lines)
    assert guard is not None
    # Guard is facing up
    direction = (-1, 0)

    # Get path of guard
    path, in_loop = walk_guard(grid, guard, direction)
    assert not in_loop

    # Count the unique positions along the path
    return len(set(pos for pos, _ in path))


def aoc2024_day06_part2(lines: Iterable[str]) -> int:
    grid, guard = parse_grid(lines)
    assert guard is not None
    guard_start = guard
    # Guard is facing up
    direction = (-1, 0)

    # Get path of guard without obstacles
    path, in_loop = walk_guard(grid, guard, direction)
    assert not in_loop

    obstacles: set[Vector] = set()
    good_obstacles: set[Vector] = set()
    # For each point along the path
    for (pos_r, pos_c), (dir_r, dir_c) in path:
        obstacle = (pos_r + dir_r, pos_c + dir_c)
        if (
            # Skip if obstacle is over the guard's starting position...
            obstacle == guard_start
            # ...or obstacle was tried already...
            or obstacle in obstacles
            # ...or obstacle is outside of grid...
            or obstacle not in grid
            # ...or an obstacle is already there
            or grid[obstacle] == "#"
        ):
            continue
        obstacles.add(obstacle)

        # Skip to first time the guard runs into this obstacle
        guard, direction = next(
            ((r, c), (dr, dc))
            for (r, c), (dr, dc) in path
            if (r + dr, c + dc) == obstacle
        )

        # If this obstacle makes the guard loop, count it
        _, in_loop = walk_guard(grid, guard, direction, obstacle=obstacle)
        if in_loop:
            good_obstacles.add(obstacle)

    # Count the number of obstacles that made the guard loop
    return len(good_obstacles)


parts = (aoc2024_day06_part1, aoc2024_day06_part2)
