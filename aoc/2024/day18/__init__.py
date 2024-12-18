from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from functools import partial
from heapq import heappop, heappush
from typing import TypeAlias


Vector: TypeAlias = tuple[int, int]
Memory: TypeAlias = tuple[set[Vector], Vector]
# PathState is a tuple of only a position
PathState: TypeAlias = tuple[Vector]
OFFSETS: tuple[Vector, ...] = ((0, -1), (0, 1), (-1, 0), (1, 0))


def iter_next_states(
        path_state: PathState,
        memory: Memory,
) -> Iterator[tuple[int, PathState]]:
    """
    Iterate through the possible next states for the current path state,
    and their weights.
    """
    ((x, y),) = path_state
    corrupted, (max_x, max_y) = memory

    for dx, dy in OFFSETS:
        nx, ny = x + dx, y + dy
        # Skip if blocked by edge
        if not (0 <= nx <= max_x and 0 <= ny <= max_y):
            continue
        # Skip if blocked by corrupted memory location
        if (nx, ny) in corrupted:
            continue

        # Try moving in this direction (costs 1)
        yield 1, ((nx, ny),)


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


def aoc2024_day18_part1(lines: Iterable[str]) -> int:
    # Process 1024 corrupted memory locations
    corrupted: set[tuple[int, int]] = set()
    for line in lines:
        if len(corrupted) >= 1024:
            break
        x, y = map(int, line.split(","))
        corrupted.add((x, y))
    max_x = max(x for x, _ in corrupted)
    max_y = max(y for _, y in corrupted)

    # Find the cost of the shortest path
    cost, _ = find_shortest_paths(
        start_state=((0, 0),),
        end_pos=(max_x, max_y),
        get_next_states=partial(
            iter_next_states,
            memory=(corrupted, (max_x, max_y)),
        ),
    )
    return cost


def aoc2024_day18_part2(lines: Iterable[str]) -> str:
    line_iter = iter(lines)
    # Process 1024 corrupted memory locations
    corrupted: set[tuple[int, int]] = set()
    for line in line_iter:
        if len(corrupted) >= 1024:
            break
        x, y = map(int, line.split(","))
        corrupted.add((x, y))
    max_x = max(x for x, _ in corrupted)
    max_y = max(y for _, y in corrupted)

    x, y = None, None
    while True:
        # Try finding some shortest path
        try:
            _, paths = find_shortest_paths(
                start_state=((0, 0),),
                end_pos=(max_x, max_y),
                get_next_states=partial(
                    iter_next_states,
                    memory=(corrupted, (max_x, max_y)),
                ),
            )
        # If a shortest path could not be found
        except RuntimeError:
            # Return the last corrupted memory location
            assert x is not None and y is not None
            return f"{x},{y}"

        # Create a set of positions along the first path
        path = {pos for (pos,) in next(paths)}
        # Corrupt more memory locations until some position along that
        # path is corrupted
        # NOTE This is way faster than only corrupting one location per
        # loop, because the shortest path algorithm can take a while.
        while True:
            x, y = map(int, next(line_iter).split(","))
            corrupted.add((x, y))
            if (x, y) in path:
                break


parts = (aoc2024_day18_part1, aoc2024_day18_part2)
