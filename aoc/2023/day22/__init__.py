from collections import defaultdict
from collections.abc import Iterable
from itertools import product
from typing import NamedTuple


class Point2D(NamedTuple):
    x: int
    y: int


class Point3D(NamedTuple):
    x: int
    y: int
    z: int


class Brick(NamedTuple):
    min_coords: Point3D
    max_coords: Point3D


def parse_bricks(lines: Iterable[str]) -> tuple[
    int, defaultdict[int, set[int]], defaultdict[int, set[int]],
]:
    """
    Parse a list of lines into information about bricks.

    The information returned will be a tuple containing the number of
    bricks, a `defaultdict` of indices of bricks that each brick
    supports, and a `defaultdict` of indices of bricks that each brick
    is supported by.
    """
    bricks: list[Brick] = []
    # Create the initial list of bricks
    for line in lines:
        coord1_str, coord2_str = line.split("~")
        brick = Brick(
            Point3D(*map(int, coord1_str.split(","))),
            Point3D(*map(int, coord2_str.split(","))),
        )
        bricks.append(brick)
    # Z-sort the list of bricks
    bricks.sort(key=lambda b: b.min_coords.z)

    # Brick indices supporting and supported by other brick indices
    supports: defaultdict[int, set[int]] = defaultdict(set)
    supported_by: defaultdict[int, set[int]] = defaultdict(set)
    # Height and index of brick at each X/Y point
    # NOTE: Here, a brick index of -1 signifies the floor.
    heights: defaultdict[Point2D, tuple[int, int]] = defaultdict(
        lambda: (0, -1),
    )

    # For each brick going up
    for i, brick in enumerate(bricks):
        (min_x, min_y, min_z), (max_x, max_y, max_z) = brick

        max_height = 0
        brick_supported_by: set[int] = set()
        # For each brick coordinate
        for x, y in product(range(min_x, max_x + 1), range(min_y, max_y + 1)):
            height, j = heights[Point2D(x, y)]
            # If the height here is greatest
            if height > max_height:
                max_height = height
                # Whichever brick was here is supporting this brick, and
                # no others
                brick_supported_by = set([j])
            # If the height here matches the previously found max
            elif height == max_height:
                # Whichever brick was here is supporting this brick
                brick_supported_by.add(j)

        # This brick is supported by the bricks it's supported by
        supported_by[i] = brick_supported_by
        # Each brick this brick is supported by supports this brick
        for j in brick_supported_by:
            supports[j].add(i)

        # The new height at each brick coordinate is the previous max
        # height, plus the height of the brick
        z = max_height + max_z - min_z + 1
        for x, y in product(range(min_x, max_x + 1), range(min_y, max_y + 1)):
            heights[Point2D(x, y)] = (z, i)

    return len(bricks), supports, supported_by


def aoc2023_day22_part1(lines: Iterable[str]) -> int:
    brick_count, supports, supported_by = parse_bricks(lines)

    total = 0
    # For each brick
    for i in range(brick_count):
        # If this brick isn't the only thing supporting the other bricks
        # that it supports
        if not any(len(supported_by[j]) == 1 for j in supports[i]):
            # This brick can be safely disintegrated
            total += 1

    return total


def aoc2023_day22_part2(lines: Iterable[str]) -> int:
    brick_count, _, supported_by = parse_bricks(lines)

    total = 0
    # For each brick
    for i in range(brick_count):
        # Imagine that this brick is disintegrated
        falling_bricks = set([i])
        # For each possibly higher brick
        for j in range(i + 1, brick_count):
            # If this higher brick is only supported by falling bricks
            if supported_by[j].issubset(falling_bricks):
                # This higher brick is also falling
                falling_bricks.add(j)

        # Add the number of falling bricks (minus the disintegrated one)
        total += len(falling_bricks) - 1

    return total


parts = (aoc2023_day22_part1, aoc2023_day22_part2)
