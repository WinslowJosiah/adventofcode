from collections.abc import Iterable, Sequence
from itertools import pairwise


def shoelace(points: Sequence[tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon, given the coordinates of its
    points in a clockwise (or counter-clockwise) order.

    The area is calculated using the "shoelace formula".
    """
    return abs(sum(
        (x1 * y2) - (y1 * x2)
        for (x1, y1), (x2, y2) in pairwise(tuple(points) + (points[0],))
    )) / 2


def aoc2023_day18_part1(lines: Iterable[str]) -> int:
    import re

    # This regex matches digging instructions, and groups the direction
    # and number of meters
    dig_regex = re.compile(r"([DLRU]) (\d+) \(#[0-9a-f]{6}\)")

    # Vertices of the polygonal trench
    points: list[tuple[int, int]] = []
    # Perimeter of boundary (or number of boundary points)
    boundary = 0
    # Current relative coordinates of the digger
    dig_x, dig_y = 0, 0
    # For each line of digging instructions
    for line in lines:
        # Extract instructions from line
        re_match = dig_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        direction, run = re_match.groups()
        run = int(run)

        # Execute the digging instructions
        match direction:
            case "R":
                dig_x += run
            case "D":
                dig_y += run
            case "L":
                dig_x -= run
            case "U":
                dig_y -= run
            case _:
                pass
        # This point is a vertex
        points.append((dig_x, dig_y))
        # This line is now on the boundary
        boundary += run
    # Hopefully the digging instructions actually form a loop!
    assert (dig_x, dig_y) == (0, 0)

    # NOTE: According to Pick's theorem (and a bit of algebra), this is
    # how to calculate the number of both interior and boundary points. 
    return int(shoelace(points)) + boundary // 2 + 1


def aoc2023_day18_part2(lines: Iterable[str]) -> int:
    import re

    # This regex matches digging instructions, and groups the relevant
    # parts of the hex color
    dig_regex = re.compile(r"[DLRU] \d+ \(#([0-9a-f]{5})([0-9a-f])\)")

    # Vertices of the polygonal trench
    points: list[tuple[int, int]] = []
    # Perimeter of boundary (or number of boundary points)
    boundary = 0
    # Current relative coordinates of the digger
    dig_x, dig_y = 0, 0
    # For each line of digging instructions
    for line in lines:
        # Extract instructions from line
        re_match = dig_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        run, direction = re_match.groups()
        run = int(run, base=16)

        # Execute the digging instructions
        match direction:
            case "0":
                dig_x += run
            case "1":
                dig_y += run
            case "2":
                dig_x -= run
            case "3":
                dig_y -= run
            case _:
                pass
        # This point is a vertex
        points.append((dig_x, dig_y))
        # This line is now on the boundary
        boundary += run
    # Hopefully the digging instructions actually form a loop!
    assert (dig_x, dig_y) == (0, 0)

    # NOTE: According to Pick's theorem (and a bit of algebra), this is
    # how to calculate the number of both interior and boundary points. 
    return int(shoelace(points)) + boundary // 2 + 1


parts = (aoc2023_day18_part1, aoc2023_day18_part2)
