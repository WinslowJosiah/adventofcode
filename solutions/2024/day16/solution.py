# https://adventofcode.com/2024/day/16

from collections.abc import Iterator

from ...base import StrSplitSolution, answer
from ...utils.grids import parse_grid, GridPoint, Direction, Position
from ...utils.pathfinding import find_shortest_paths


class State(Position):
    # NOTE find_shortest_paths needs a state with a node property.
    @property
    def node(self) -> GridPoint:
        return self.point


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 16.
    """
    _year = 2024
    _day = 16

    @answer((109496, 551))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, ignore_chars="#")
        start_node = next(k for k, v in grid.items() if v == "S")
        end_node = next(k for k, v in grid.items() if v == "E")

        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            # Turn 90 degrees clockwise = 1000 points
            yield s.rotate("CW"), 1000
            # Turn 90 degrees counter-clockwise = 1000 points
            yield s.rotate("CCW"), 1000
            # Move forward = 1 point
            if s.next_point in grid:
                yield s.step(), 1

        path_result = find_shortest_paths(
            [State(start_node, Direction.RIGHT)],
            end_node,
            get_transitions=get_transitions,
        )
        all_nodes = set(
            state.node
            for path in path_result.paths
            for state in path
        )
        return path_result.distance, len(all_nodes)
