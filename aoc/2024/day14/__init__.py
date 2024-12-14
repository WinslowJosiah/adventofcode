from collections.abc import Iterable
from typing import cast, TypeAlias


Vector: TypeAlias = tuple[int, int]
Robot: TypeAlias = tuple[Vector, Vector]


def parse_input(lines: Iterable[str]) -> tuple[list[Robot], int, int]:
    """
    Parse the input, and return a list of robots, as well as the width
    and height of their space.

    The width and height are assumed to be as small as possible to
    contain the initial configuration of robots.
    """
    robots: list[Robot] = []
    for line in lines:
        p_string, v_string = line.split()
        p = cast(Vector, tuple(
            map(int, p_string.removeprefix("p=").split(","))
        ))
        v = cast(Vector, tuple(
            map(int, v_string.removeprefix("v=").split(","))
        ))
        robots.append((p, v))

    width = max(px for (px, _), _ in robots) + 1
    height = max(py for (_, py), _ in robots) + 1
    return (robots, width, height)


def aoc2024_day14_part1(lines: Iterable[str]) -> int:
    from math import prod

    robots, width, height = parse_input(lines)

    quadrants = [0 for _ in range(4)]
    for (px, py), (vx, vy) in robots:
        # Calculate this robot's position after 100 seconds
        endx = (px + vx * 100) % width
        endy = (py + vy * 100) % height
        # If the robot is exactly between quadrants, don't count it
        if endx == width // 2 or endy == height // 2:
            continue

        # Tally this robot in the correct quadrant
        qx = endx // (width // 2 + 1)
        qy = endy // (height // 2 + 1)
        quadrants[qy * 2 + qx] += 1

    return prod(quadrants)


def aoc2024_day14_part2(lines: Iterable[str]) -> int:
    robots, width, height = parse_input(lines)

    # NOTE The largest number of seconds to wait before seeing the
    # picture is the number of tiles, because the configurations will
    # loop after at most that long.
    for second in range(1, width * height + 1):
        # Calculate each robot's position after a second
        robots = [
            (
                ((px + vx) % width, (py + vy) % height),
                (vx, vy),
            )
            for (px, py), (vx, vy) in robots
        ]
        # If every robot is in a unique position
        if len({p for p, _ in robots}) == len(robots):
            # There's the picture!
            # NOTE I have no idea how I was supposed to know what this
            # condition was.
            return second

    assert False  # We should never get here


parts = (aoc2024_day14_part1, aoc2024_day14_part2)
