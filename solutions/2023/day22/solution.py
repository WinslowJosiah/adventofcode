# https://adventofcode.com/2023/day/22

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import product
from typing import Self

from ...base import StrSplitSolution, answer


type Cube = tuple[int, int, int]


@dataclass
class Brick:
    id_: int
    cubes: set[Cube]

    @property
    def lowest_z(self) -> int:
        return min(z for _, _, z in self.cubes)

    @classmethod
    def parse(cls, id_: int, line: str) -> Self:
        start, end = (point.split(",") for point in line.split("~"))
        dim_ranges = [range(int(l), int(r) + 1) for l, r in zip(start, end)]
        cubes = {(x, y, z) for x, y, z in product(*dim_ranges)}
        return cls(id_, cubes)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 22.
    """
    _year = 2023
    _day = 22

    @answer((492, 86556))
    def solve(self) -> tuple[int, int]:
        # Sort bricks from lowest to highest
        bricks = sorted(
            (Brick.parse(i, line) for i, line in enumerate(self.input)),
            key=lambda b: b.lowest_z,
        )

        # NOTE The default height here is 0, meaning the ground.
        height_map: dict[tuple[int, int], int] = defaultdict(int)
        # Make each brick fall until it hits the ground or another brick
        for brick in bricks:
            target_z = max(height_map[x, y] + 1 for x, y, _ in brick.cubes)
            delta_z = brick.lowest_z - target_z
            brick.cubes = {(x, y, z - delta_z) for x, y, z in brick.cubes}
            # Update the height map with the new settled brick
            for x, y, z in brick.cubes:
                height_map[x, y] = max(height_map[x, y], z)

        cube_to_brick_id = {
            cube: brick.id_
            for brick in bricks
            for cube in brick.cubes
        }
        # Find out which bricks support which other bricks
        supports: dict[int, set[int]] = {}
        supported_by: dict[int, set[int]] = defaultdict(set)
        for brick in bricks:
            cubes_above = {(x, y, z + 1) for x, y, z in brick.cubes}
            bottom_id = brick.id_
            top_ids = {
                top_id
                for cube in cubes_above
                if (top_id := cube_to_brick_id.get(cube)) is not None
                and top_id != bottom_id
            }
            # NOTE It's helpful to have a mapping in both directions.
            supports[bottom_id] = top_ids
            for top_id in top_ids:
                supported_by[top_id].add(bottom_id)

        # If a top brick is only supported by one bottom brick, that
        # bottom brick is a "load bearer" and cannot be safely removed
        load_bearers = {
            bottom_id
            for _, bottom_ids in supported_by.items()
            for bottom_id in bottom_ids
            if len(bottom_ids) == 1
        }
        num_removable_bricks = len(bricks) - len(load_bearers)

        num_falling_bricks = 0
        # For each "load bearer" brick
        for brick_id in load_bearers:
            removed = {brick_id}
            # Find all other bricks that would fall if it were removed
            queue = deque(supports[brick_id])
            while queue:
                other_id = queue.popleft()
                if other_id in removed:
                    continue
                # If we've removed all supporters of this brick, it will
                # fall; remove it too, and check the bricks it supports
                if supported_by[other_id].issubset(removed):
                    removed.add(other_id)
                    queue.extend(supports[other_id])
            # NOTE We subtract 1 here because we don't count the initial
            # brick that was removed.
            num_falling_bricks += len(removed) - 1

        return num_removable_bricks, num_falling_bricks
