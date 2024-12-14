from collections.abc import Iterable
from math import prod
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


def get_safety_index(robots: Iterable[Robot], width: int, height: int) -> int:
    quadrants = [0] * 4
    for (px, py), _ in robots:
        # If the robot is exactly between quadrants, don't count it
        if px == width // 2 or py == height // 2:
            continue
        # Tally this robot in the correct quadrant
        qx = px // (width // 2 + 1)
        qy = py // (height // 2 + 1)
        quadrants[qy * 2 + qx] += 1
    return prod(quadrants)


def aoc2024_day14_part1(lines: Iterable[str]) -> int:
    robots, width, height = parse_input(lines)

    # Simulate the robots' positions after 100 seconds
    robots = [
        (
            ((px + vx * 100) % width, (py + vy * 100) % height),
            (vx, vy),
        )
        for (px, py), (vx, vy) in robots
    ]
    return get_safety_index(robots, width, height)


def aoc2024_day14_part2(lines: Iterable[str]) -> int:
    robots, width, height = parse_input(lines)

    # NOTE The largest number of seconds to wait before seeing the
    # picture is the number of tiles, because the configurations will
    # loop after at most that long.
    safety_indices: list[int] = []
    for _ in range(width * height + 1):
        safety_indices.append(get_safety_index(robots, width, height))

        # Calculate each robot's position after another second
        robots = [
            (
                ((px + vx) % width, (py + vy) % height),
                (vx, vy),
            )
            for (px, py), (vx, vy) in robots
        ]

    # NOTE The safety index will (probably) be the lowest at the point
    # when the picture shows up. (I found this approach after looking at
    # someone's code golf solution.) I have no idea how I was supposed
    # to figure this out.
    return min(
        range(len(safety_indices)),
        key=safety_indices.__getitem__,
    )


parts = (aoc2024_day14_part1, aoc2024_day14_part2)
