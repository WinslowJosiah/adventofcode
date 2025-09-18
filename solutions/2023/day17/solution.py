# https://adventofcode.com/2023/day/17

from collections.abc import Iterator
from typing import NamedTuple

from ...base import StrSplitSolution, answer, slow
from ...utils.grids import Direction, GridPoint, Position, parse_grid
from ...utils.pathfinding import find_shortest_paths, taxicab_distance


class State(NamedTuple):
    pos: Position
    steps: int

    # NOTE find_shortest_paths needs a state with a node property.
    @property
    def node(self) -> GridPoint:
        return self.pos.point


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 17.
    """
    _year = 2023
    _day = 17

    def _solve(self, min_steps: int, max_steps: int) -> int:
        grid = parse_grid(self.input, int)
        start_node = 0, 0
        end_node = len(self.input) - 1, len(self.input[-1]) - 1

        def is_valid_state(s: State) -> bool:
            # - Position must be in grid
            # - End cannot be reached before minimum steps are taken
            return s.pos.point in grid and (
                s.steps >= min_steps or s.node != end_node
            )

        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            if s.node != start_node and s.steps >= min_steps:
                # Turn left (and reset number of steps)
                next_pos = s.pos.rotate("CCW").step()
                next_state = State(next_pos, steps=1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]

                # Turn right (and reset number of steps)
                next_pos = s.pos.rotate("CW").step()
                next_state = State(next_pos, steps=1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]

            if s.steps < max_steps:
                # Move forward (and increase number of steps)
                next_pos = s.pos.step()
                next_state = State(next_pos, steps=s.steps + 1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]

        path_result = find_shortest_paths(
            start_states=[
                State(Position(start_node, Direction.RIGHT), steps=0),
                State(Position(start_node, Direction.DOWN), steps=0),
            ],
            end_node=end_node,
            get_transitions=get_transitions,
            heuristic=taxicab_distance,
        )
        return path_result.distance

    @answer(771)
    def part_1(self) -> int:
        return self._solve(0, 3)

    @answer(930)
    @slow
    def part_2(self) -> int:
        return self._solve(4, 10)
