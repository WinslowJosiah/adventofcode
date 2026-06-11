# https://adventofcode.com/2024/day/14

from collections import Counter
from dataclasses import dataclass
from math import prod
import re
from typing import Self

from ...base import StrSplitSolution, answer, slow


@dataclass
class Robot:
    px: int
    py: int
    vx: int
    vy: int

    def step(self, width: int, height: int):
        """Move robot forward by one second."""
        self.px = (self.px + self.vx) % width
        self.py = (self.py + self.vy) % height

    @classmethod
    def from_line(cls, line: str) -> Self:
        return cls(*map(int, re.findall(r"-?\d+", line)))


def safety_factor(robots: list[Robot], width: int, height: int) -> int:
    mid_x, mid_y = width // 2, height // 2

    quadrants = Counter(
        (robot.px > mid_x, robot.py > mid_y)
        for robot in robots
        if robot.px != mid_x and robot.py != mid_y
    )
    return prod(quadrants.values())


def robots_to_grid_str(robots: list[Robot], width: int, height: int) -> str:
    grid = Counter((robot.px, robot.py) for robot in robots)
    return "\n".join(
        "".join(str(grid.get((x, y), ".")) for x in range(width))
        for y in range(height)
    )


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 14.
    """
    _year = 2024
    _day = 14

    @answer((210587128, 7286))
    @slow
    def solve(self) -> tuple[int, int]:
        width, height = (11, 7) if self.testing else (101, 103)
        robots = [Robot.from_line(line) for line in self.input]

        part_1, part_2 = None, None
        for second in range(max(width * height, 100) + 1):
            grid_str = robots_to_grid_str(robots, width, height)

            if second == 100:
                print("Robots after 100 seconds:")
                print(grid_str)
                print()
                part_1 = safety_factor(robots, width, height)

            # HACK Because we know the Christmas tree has a solid border
            # around it, we can simply check whether this border exists.
            if "1" * 31 in grid_str:
                print(f"Christmas tree found after {second} seconds:")
                print(grid_str)
                print()
                part_2 = second

            if part_1 is not None and part_2 is not None:
                break

            for robot in robots:
                robot.step(width, height)
        else:
            assert part_1 is not None, "failed to simulate 100 seconds"
            assert part_2 is not None, "Christmas tree Easter egg not found"

        return part_1, part_2
