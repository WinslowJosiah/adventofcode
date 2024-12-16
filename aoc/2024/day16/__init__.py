from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from functools import partial
from heapq import heappop, heappush
from typing import TypeAlias


# NOTE I would make the coordinates be complex numbers, but comparisons
# with them raise a TypeError, and heapq will make comparisons with
# tuples that contain these "vectors".
Vector: TypeAlias = tuple[int, int]
Grid: TypeAlias = defaultdict[Vector, str]
# PathState is a tuple of position and direction
PathState: TypeAlias = tuple[Vector, Vector]


def parse_input(lines: Iterable[str]) -> tuple[Grid, Vector, Vector]:
    """
    Parse the input, and return a grid, a starting position, and an
    ending position.
    """
    grid: Grid = defaultdict(lambda: "#")
    start_pos, end_pos = None, None
    for r, row in enumerate(lines):
        for c, tile in enumerate(row):
            pos = (r, c)
            if tile == "S":
                start_pos = pos
            elif tile == "E":
                end_pos = pos
            grid[pos] = tile
    assert start_pos is not None and end_pos is not None
    return grid, start_pos, end_pos


def iter_next_states(
        state: PathState,
        grid: Grid,
) -> Iterator[tuple[int, PathState]]:
    """
    Iterate through the possible next states for the current path state,
    and their weights.
    """
    (node_r, node_c), (dir_r, dir_c) = state
    # Try turning 90 degrees to the right (1000 points)
    yield 1000, ((node_r, node_c), (dir_c, -dir_r))
    # Try turning 90 degrees to the left (1000 points)
    yield 1000, ((node_r, node_c), (-dir_c, dir_r))
    # Try moving forward (1 point)
    next_node = (node_r + dir_r, node_c + dir_c)
    if grid[next_node] != "#":
        yield 1, (next_node, (dir_r, dir_c))


def find_shortest_paths(
        start_state: PathState,
        end_pos: Vector,
        get_next_states: Callable[
            [PathState], Iterable[tuple[int, PathState]]
        ],
) -> tuple[int, Iterator[list[PathState]]]:
    """
    Find the shortest path between two points in a weighted graph using
    Dijkstra's algorithm.

    In this case, the path states include the current facing direction.
    The search concludes when `end_pos` is reached, regardless of the
    rest of the path state. For each possible next path state,
    `get_next_states` should return both its cost and the state itself.
    """
    # Lowest costs to get to each state
    costs: dict[PathState, int] = {}
    # Queue of states left to search from
    # NOTE Using the heapq library, we can treat this like a priority
    # queue, which allows the minimum item to be efficiently removed
    # in each iteration of the search.
    priority_queue: list[tuple[int, PathState]] = [(0, start_state)]
    # Previous states for each visited state
    # NOTE This will help in reconstructing each path later; this could
    # be omitted if that isn't needed.
    prev_states: defaultdict[PathState, set[PathState]] = defaultdict(set)

    while priority_queue:
        cost, state = heappop(priority_queue)
        # Stop searching if end position was reached
        pos, *_ = state
        if pos == end_pos:
            break
        # For each possible next state and its weight
        for weight, next_state in get_next_states(state):
            prev_cost = costs.get(next_state, float("inf"))
            next_cost = cost + weight
            # If we've found a lower-cost way to get to this state
            if next_cost < prev_cost:
                # Update its cost and continue searching from here
                costs[next_state] = next_cost
                heappush(priority_queue, (next_cost, next_state))
                # Reset the previous states (they didn't count)
                prev_states[next_state] = {state}
            # If we've found a same-cost way to get to this state
            elif next_cost == prev_cost:
                # This state is the next state's previous state
                prev_states[next_state].add(state)
    else:
        raise RuntimeError("no path exists!")

    start_node, *_ = start_state
    # Walk backwards down each path from the end to the start
    # NOTE Making this function return an iterator instead of a list
    # means the paths won't be walked down unless we tell it to, making
    # it faster if we don't need the paths.
    def walk(state: PathState) -> Iterator[list[PathState]]:
        node, *_ = state
        if node == start_node:
            yield [state]
            return
        for prev_state in prev_states[state]:
            for path in walk(prev_state):
                yield path + [state]

    return cost, walk(state)


def aoc2024_day16_part1(lines: Iterable[str]) -> int:
    grid, start_pos, end_pos = parse_input(lines)
    cost, _ = find_shortest_paths(
        # The reindeer starts moving east
        start_state=(start_pos, (0, 1)),
        end_pos=end_pos,
        get_next_states=partial(iter_next_states, grid=grid),
    )
    return cost


def aoc2024_day16_part2(lines: Iterable[str]) -> int:
    grid, start_pos, end_pos = parse_input(lines)
    _, paths = find_shortest_paths(
        # The reindeer starts moving east
        start_state=(start_pos, (0, 1)),
        end_pos=end_pos,
        get_next_states=partial(iter_next_states, grid=grid),
    )
    # Count unique positions along all paths
    return len({pos for path in paths for pos, _ in path})


parts = (aoc2024_day16_part1, aoc2024_day16_part2)
