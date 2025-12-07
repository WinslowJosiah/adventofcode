# https://adventofcode.com/2025/day/7

from collections import Counter, deque

from ...base import StrSplitSolution, answer
from ...utils.grids import Direction, GridPoint, Position, parse_grid


class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        next_beam = self.step()
        # Split beam at splitter; otherwise, continue forward
        if char == "^":
            return [
                next_beam.rotate("CW").step().rotate("CCW"),
                next_beam.rotate("CCW").step().rotate("CW"),
            ]
        return [next_beam]


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 7.
    """
    _year = 2025
    _day = 7

    @answer((1585, 16716444407407))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        start = Beam(
            next(k for k, v in grid.items() if v == "S"),
            Direction.DOWN,
        )

        # NOTE BFS is the best way to track the beams, as all beams will
        # be moving down at the same rate and won't lag behind.
        beams = deque([start])
        seen: set[Beam] = set()

        num_splits = 0
        timelines = Counter([start.point])
        bottom_points: list[GridPoint] = []
        while beams:
            current_beam = beams.popleft()

            next_beams = current_beam.next_beams(grid[current_beam.point])
            # If the current beam has more than one possible next beam,
            # it has split
            if len(next_beams) > 1:
                num_splits += 1

            for next_beam in next_beams:
                # Track beam points as they leave the bottom
                if next_beam.point not in grid:
                    bottom_points.append(current_beam.point)
                    continue

                # This next beam's point has now been reached in all
                # timelines that have reached the current beam
                timelines[next_beam.point] += timelines[current_beam.point]

                if next_beam in seen:
                    continue
                seen.add(next_beam)
                beams.append(next_beam)

        num_bottom_timelines = sum(timelines[point] for point in bottom_points)
        return num_splits, num_bottom_timelines
