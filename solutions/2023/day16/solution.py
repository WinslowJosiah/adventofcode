# https://adventofcode.com/2023/day/16

from functools import cache

from ...base import StrSplitSolution, answer
from ...utils.grids import Grid, Direction, Position, parse_grid


class Beam(Position):
    @cache
    def next_beams(self, char: str) -> list["Beam"]:
        match char:
            # Empty space: ignore
            case ".":
                return [self.step()]
            # Pointy end of splitter: ignore
            case "-" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.step()]
            case "|" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.step()]
            # Flat side of splitter: split
            case "-" | "|":
                return [self.rotate("CCW").step(), self.rotate("CW").step()]
            # Mirror: reflect
            case "/" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate("CCW").step()]
            case "/" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate("CW").step()]
            case "\\" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate("CW").step()]
            case "\\" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate("CCW").step()]
            # Unknown char: error out
            case _:
                raise ValueError(
                    f"can't find next states from {self} and {char=}"
                )


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 16.
    """
    _year = 2023
    _day = 16

    _cached_functions = (Beam.next_beams,)

    def _solve(self, grid: Grid[str], start: Beam) -> int:
        seen: set[Beam] = set()
        beams: list[Beam] = [start]
        while beams:
            current = beams.pop()
            if current in seen:
                continue
            seen.add(current)

            for next_beam in current.next_beams(grid[current.point]):
                if next_beam.point in grid:
                    beams.append(next_beam)

        # Count unique energized tiles
        return len({beam.point for beam in seen})

    @answer(7067)
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        # At top-left corner, facing right
        return self._solve(grid, Beam((0, 0), Direction.RIGHT))

    @answer(7324)
    def part_2(self) -> int:
        grid_height = len(self.input)
        grid_width = len(self.input[0])
        grid = parse_grid(self.input)

        return max(
            # At top, facing down
            *(
                self._solve(grid, Beam((0, col), Direction.DOWN))
                for col in range(grid_width)
            ),
            # At right, facing left
            *(
                self._solve(grid, Beam((row, grid_width - 1), Direction.LEFT))
                for row in range(grid_height)
            ),
            # At bottom, facing up
            *(
                self._solve(grid, Beam((grid_height - 1, col), Direction.UP))
                for col in range(grid_width)
            ),
            # At left, facing right
            *(
                self._solve(grid, Beam((row, 0), Direction.RIGHT))
                for row in range(grid_height)
            ),
        )
