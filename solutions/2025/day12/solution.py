# https://adventofcode.com/2025/day/12

import re

from ...base import TextSolution, answer


class Solution(TextSolution):
    """
    Solution for Advent of Code 2025 Day 12.
    """
    _year = 2025
    _day = 12

    @answer(555)
    def part_1(self) -> int:
        SHAPE_WIDTH = SHAPE_HEIGHT = 3
        *raw_shapes, raw_regions = self.input.split("\n\n")

        # Get the number of tiles in each shape
        shape_num_tiles: list[int] = []
        for raw_shape in raw_shapes:
            _, *grid = raw_shape.splitlines()
            assert len(grid) == SHAPE_HEIGHT
            assert all(len(row) == SHAPE_WIDTH for row in grid)
            shape_num_tiles.append(
                sum(ch == "#" for row in grid for ch in row)
            )

        total = 0
        for raw_region in raw_regions.splitlines():
            width, height, *shape_quantities = (
                map(int, re.findall(r"\d+", raw_region))
            )

            # If this amount of presents definitely fits, add to tally
            max_presents_lower_bound = (
                (width // SHAPE_WIDTH) * (height // SHAPE_HEIGHT)
            )
            num_presents = sum(shape_quantities)
            if num_presents <= max_presents_lower_bound:
                total += 1
                continue

            # Skip if lower bound of tile count won't fit in the region
            num_tiles_lower_bound = sum(
                tiles * quantity
                for tiles, quantity in zip(shape_num_tiles, shape_quantities)
            )
            region_num_tiles = width * height
            if num_tiles_lower_bound > region_num_tiles:
                continue

            # HACK Anything more, and we'd have to use some NP-complete
            # algorithm. Luckily, our input only has easy cases.
            assert False, "shape packing is complicated"

        return total
