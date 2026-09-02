# https://adventofcode.com/2024/day/18

from collections.abc import Iterator
from itertools import islice
from typing import cast, NamedTuple

from ...base import StrSplitSolution, answer
from ...utils.grids import GridPoint, neighbors
from ...utils.pathfinding import find_shortest_paths, NoPathError


# NOTE find_shortest_paths needs a state with a node property.
class State(NamedTuple):
    node: GridPoint


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 18.
    """
    _year = 2024
    _day = 18

    @answer((268, "64,11"))
    def solve(self) -> tuple[int, str]:
        GRID_SIZE, NUM_INITIAL_BYTES = (7, 12) if self.testing else (71, 1024)

        coords = iter(
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        )
        # Simulate corrupting the initial bytes
        corrupted = set(islice(coords, NUM_INITIAL_BYTES))

        # Prepare the arguments to find_shortest_paths
        start_states = [State((0, 0))]
        end_node = (GRID_SIZE - 1, GRID_SIZE - 1)
        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            for n in neighbors(s.node, num_directions=4, grid_size=GRID_SIZE):
                if n not in corrupted:
                    yield State(n), 1

        min_steps, first_blocker = None, None
        while True:
            # Find the shortest path through the grid at this point;
            # exit infinite loop if no path exists
            try:
                path_result = find_shortest_paths(
                    start_states=start_states,
                    end_node=end_node,
                    get_transitions=get_transitions,
                )
            except NoPathError:
                break

            # Save the length of the shortest path if not saved before
            if min_steps is None:
                min_steps = path_result.distance

            # Choose an arbitrary path
            path = next(path_result.paths)
            path_nodes = set(state.node for state in path)
            # Corrupt more bytes until this path is blocked
            # NOTE This is faster than corrupting only one byte at a
            # time, because we don't run find_shortest_paths() as often.
            for coord in coords:
                corrupted.add(coord)
                if coord in path_nodes:
                    first_blocker = coord
                    break
            else:
                raise RuntimeError("no blocking byte found")

        assert min_steps is not None and first_blocker is not None
        return min_steps, ",".join(map(str, first_blocker))
