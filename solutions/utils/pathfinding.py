# pyright: reportArgumentType=false
from collections.abc import Callable, Hashable, Iterable, Iterator
from collections import defaultdict, deque
from dataclasses import dataclass
from heapq import heapify, heappop, heappush
from itertools import chain, count
from typing import Protocol, Self

from ..utils.grids import taxicab_distance


class _PositiveInfinity:
    """
    Class representing positive infinity for comparisons.

    This is a hack to allow a positive infinity-like value to be used in
    type hints without resorting to the more general type hint `float`.
    """
    def __new__(cls) -> Self:
        # NOTE This class is a singleton.
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return type(self).__name__.removeprefix("_")

    def __lt__(self, other: object) -> bool:
        if isinstance(other, int):
            return False
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, int):
            return True
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, int):
            return False
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, int):
            return True
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        return self is other


class PathState[Node](Hashable, Protocol):
    """
    Protocol defining the interface for states used in pathfinding.

    States must have a `node` property and be hashable (e.g. NamedTuple
    or frozen dataclass).
    """
    @property
    def node(self) -> Node: ...


# HACK The type checker complains when I constrain the generic typevar
# State by PathState[Node], since Node is also a generic typevar. The
# only thing I can do about this seems to be to ignore it. (This will
# happen repeatedly throughout this module.)
@dataclass(frozen=True)
class PathResult[Node, State: PathState[Node]]:  # pyright: ignore[reportGeneralTypeIssues]
    """
    Result of `find_shortest_paths`.

    Attributes
    ----------
    distance : int
        The shortest path distance.
    num_paths : int
        Count of all shortest paths.
    all_nodes : set of node
        All unique nodes across all shortest paths.
    paths : iterator of list of state
        Iterator yielding each shortest path as a list of states.
    """
    distance: int
    num_paths: int
    all_nodes: set[Node]
    paths: Iterator[list[State]]


def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    """
    Find the shortest paths between starting states and an ending node.

    Multiple starting states can be provided, each of which must start
    at the same node; this is useful for, as an example, considering
    different orientations at the starting node. States must have a
    `node` property representing its node, and must be hashable (as they
    are hashed internally). Any state reaching the ending node is
    considered an ending state.

    If provided, the heuristic function must be a function that takes
    two nodes and returns an estimate of the distance between them. The
    heuristic function must be admissible (i.e. never overestimate the
    true distance) to guarantee finding the shortest path.

    Parameters
    ----------
    start_states : iterable of state
        States at the start of the paths. Must be non-empty. All states
        must have the same node value. States must have a `node`
        property representing its node and be hashable.
    end_node : node
        The target node. Any state with this node is an ending state.
    get_transitions : callable
        Callable that takes a state as argument, and returns an iterable
        of `(next_state, distance)` tuples. `distance` should be the
        `int` distance from the given state to `next_state`. All
        distances must be non-negative to ensure correct results.
    heuristic : callable, optional
        Admissible heuristic function that takes `(current_node,
        target_node)` as arguments and returns an estimated distance to
        reach the target. For grid-based pathfinding, Manhattan distance
        (a.k.a. taxicab distance) is commonly used.

    Returns
    -------
    PathResult
        Contains:
            - distance: int, the shortest path distance
            - num_paths: int, count of all shortest paths
            - all_nodes: set of node, all unique nodes across all
            shortest paths
            - paths: iterator yielding each shortest path as a list of
            states

    Notes
    -----
    If a heuristic is provided, A* is used; otherwise, Dijkstra's
    algorithm is used. The heuristic function must be admissible (i.e.
    never overestimate the true distance) for A* to guarantee finding
    the shortest path. Ideally, the heuristic function should be
    consistent (i.e. not decrease the total estimated distance if an
    intermediate node is reached first) for A* to explore the nodes
    optimally.

    For grid-based pathfinding, a commonly used heuristic is Manhattan
    distance (a.k.a. taxicab distance).

    Examples
    --------
    >>> # Dijkstra's algorithm (no heuristic)
    >>> result = find_shortest_paths(
    ...     start_states=start_states,
    ...     end_node=end_node,
    ...     get_transitions=get_transitions,
    ... )
    >>> # A* algorithm with taxicab distance heuristic
    >>> from .utils.pathfinding import taxicab_distance
    >>> result = find_shortest_paths(
    ...     start_states=start_states,
    ...     end_node=end_node,
    ...     get_transitions=get_transitions,
    ...     heuristic=taxicab_distance,
    ... )
    """
    start_states_set: set[State] = set(start_states)
    if not start_states_set:
        raise ValueError("start_states must be non-empty")

    # Verify all start states have the same node
    start_node = next(iter(start_states_set)).node
    if not all(s.node == start_node for s in start_states_set):
        raise ValueError("all start states must have the same node")

    distances: dict[State, int | _PositiveInfinity] = defaultdict(
        _PositiveInfinity,
        {(s, 0) for s in start_states_set},
    )
    prev_states: dict[State, set[State]] = defaultdict(set)
    # HACK The items pushed onto the priority queue must be comparable;
    # having an item from this counter between the metadata and the
    # state ensure that they are, even if states are not comparable.
    counter = count()

    # NOTE For A*, priority = distance + heuristic; for Dijkstra,
    # priority is distance.
    def get_priority(distance: int, node: Node) -> int:
        return distance + (heuristic(node, end_node) if heuristic else 0)

    priority_queue: list[tuple[int, int, int, State]] = [
        (get_priority(0, s.node), 0, next(counter), s)
        for s in start_states_set
    ]
    heapify(priority_queue)
    shortest_distance: int | None = None
    end_states: list[State] = []

    while priority_queue:
        _, distance, _, state = heappop(priority_queue)

        # If we've found an end state, record the distance
        if state.node == end_node:
            if shortest_distance is None:
                shortest_distance = distance
            # Continue until we exceed the shortest distance (so we find
            # all ending states at the same distance)
            if distance > shortest_distance:
                break
            end_states.append(state)
            continue

        # Skip if we've already found this state with a better distance
        if distances[state] < distance:
            continue

        for next_state, distance_to_next_state in get_transitions(state):
            prev_distance = distances[next_state]
            next_distance = distance + distance_to_next_state

            # If this is a lower-distance way to get here
            if next_distance < prev_distance:
                # Update distances and continue searching from here
                distances[next_state] = next_distance
                priority = get_priority(next_distance, next_state.node)
                heappush(
                    priority_queue,
                    (priority, next_distance, next(counter), next_state),
                )
                # No other path to here has been optimal yet
                prev_states[next_state].clear()

            # If this isn't a worse-distance way to get here
            if next_distance <= prev_distance:
                # The state we got here from is on an optimal path
                prev_states[next_state].add(state)

    if shortest_distance is None:
        raise ValueError("no path exists")

    # Count paths and collect nodes by traversing prev_states in reverse
    path_counts: dict[State, int] = {}
    nodes_on_paths: set[Node] = set()
    in_progress: set[Node] = set()

    def count_paths_to(state: State) -> int:
        """Count paths from any start state to `state`."""
        if state in path_counts:
            return path_counts[state]

        # HACK There could be a 0-distance cycle, which would lead to
        # infinite recursion while counting paths. So if we're asked to
        # count paths to a state we're already in the process of
        # counting paths to, we raise an error.
        if state in in_progress:
            raise ValueError(f"cycle detected at state: {state}")

        if state in start_states_set:
            path_counts[state] = 1
            nodes_on_paths.add(state.node)
            return 1

        in_progress.add(state)
        total = sum(map(count_paths_to, prev_states[state]))
        in_progress.remove(state)

        path_counts[state] = total
        nodes_on_paths.add(state.node)
        return total

    num_paths = sum(map(count_paths_to, end_states))

    # Generate actual paths lazily
    def paths_ending_at(state: State) -> Iterator[list[State]]:
        """Generate all paths ending at `state`."""
        if state in start_states_set:
            yield [state]
            return
        for prev_state in prev_states[state]:
            for path in paths_ending_at(prev_state):
                yield path + [state]

    all_paths = chain.from_iterable(map(paths_ending_at, end_states))

    return PathResult(
        distance=shortest_distance,
        num_paths=num_paths,
        all_nodes=nodes_on_paths,
        paths=all_paths,
    )


def find_reachable_nodes[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        *,
        get_next_states: Callable[[State], Iterable[State]],
        max_distance: int | None = None,
) -> set[Node]:  # pyright: ignore[reportInvalidTypeVarUse]
    """
    Find all nodes reachable from the starting states.

    This performs a breadth-first search to find all nodes that can be
    reached from any of the starting states. Optionally, a maximum
    distance can be specified to limit the search.

    Parameters
    ----------
    start_states : iterable of state
        States at the start of the search. Must be non-empty. States
        must have a `node` property representing its node and be
        hashable.
    get_next_states : callable
        Callable that takes a state as argument and returns an iterable
        of next states.
    max_distance : int, optional
        Maximum distance from any start state. If provided, only nodes
        within this distance are included. All state transitions are
        unweighted, i.e. the distance between any two states is 1.

    Returns
    -------
    set of node
        All unique nodes reachable from the starting states.
    """
    start_states_list: list[State] = list(start_states)
    if not start_states_list:
        raise ValueError("start_states must be non-empty")

    visited: set[State] = set()
    reachable: set[Node] = set()
    queue: deque[tuple[int, State]] = deque((0, s) for s in start_states_list)

    for state in start_states_list:
        visited.add(state)
        reachable.add(state.node)

    while queue:
        distance, state = queue.popleft()

        # If we've reached the maximum distance, don't explore further
        if max_distance is not None and distance >= max_distance:
            continue

        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                reachable.add(next_state.node)
                queue.append((distance + 1, next_state))

    return reachable


__all__ = [
    "PathResult",
    "PathState",
    "find_reachable_nodes",
    "find_shortest_paths",
    "taxicab_distance",
]
