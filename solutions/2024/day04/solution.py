# https://adventofcode.com/2024/day/4

from ...base import StrSplitSolution, answer
from ...utils.grids import add_points, offsets, parse_grid, subtract_points


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 4.
    """
    _year = 2024
    _day = 4

    @answer(2662)
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        # Find all start characters of an XMAS
        for start, start_char in grid.items():
            if start_char != "X":
                continue

            # Scan for the rest of the characters in all directions
            for offset in offsets(num_directions=8):
                point = start
                for char in "MAS":
                    point = add_points(point, offset)
                    if grid.get(point) != char:
                        break
                else:
                    total += 1

        return total

    @answer(2034)
    def part_2(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        # Find all center characters of an X-shaped MAS
        for center, center_char in grid.items():
            if center_char != "A":
                continue

            num_mas = 0
            # Scan for M and S in diagonal directions
            for offset in offsets(num_directions=4, diagonals=True):
                forward = add_points(center, offset)
                backward = subtract_points(center, offset)
                # MAS has M and S in opposite directions from the A
                if grid.get(forward) == "M" and grid.get(backward) == "S":
                    num_mas += 1

            # An X-MAS consists of two MASes that cross
            if num_mas == 2:
                total += 1

        return total
