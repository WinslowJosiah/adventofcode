from collections.abc import Callable, Iterable, Iterator
from heapq import heappop, heappush
from itertools import starmap
from operator import add, sub, neg


# We will represent coordinates and directions as tuples of ints
type Vector = tuple[int, ...]
# We will represent info about the current path as a tuple of this info
type PathInfo = tuple[Vector, Vector | None, int]


# This is a list of valid offsets
offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]


def find_path(
        src_node: Vector,
        dest_node: Vector,
        neighbors: Callable[
            [PathInfo, Vector], Iterable[tuple[int, PathInfo]]
        ],
) -> int:
    """
    Find the path from `src_node` to `dest_node` incurring the lowest
    cost.

    `neighbors` is a function that takes a `PathInfo` (all the relevant
    info about the current path) and a `Vector` (the destination node)
    as arguments, and yields the cost and `PathInfo` after following
    each valid neighboring node. It is in this function that paths can
    be restricted.
    """
    # NOTE: We are using a version of Dijkstra's algorithm, which finds
    # the shortest path between two nodes in a weighted graph. We have
    # to modify it to keep track of the number of moves since the last
    # left or right turn, but the principles are mostly the same.

    # This set contains every node visited so far
    visited: set[PathInfo] = set()
    # This dict associates each PathInfo with the minimum cost to
    # traverse there
    costs: dict[PathInfo, int] = {}

    # This queue stores each node that will be visited next in the path
    queue: list[tuple[int, PathInfo]] = [(0, (src_node, None, 0))]
    while queue:
        # Get the info for the path with the lowest cost so far
        cost, key = heappop(queue)

        node, *_ = key
        # If we have reached the destination node, we're done searching
        if node == dest_node:
            return cost

        # If we have already visited this node in this way
        if key in visited:
            # Skip this node
            continue
        # Mark this node as visited
        visited.add(key)

        # For each neighbor
        for weight, next_key in neighbors(key, dest_node):
            # This is the previously found cost of getting to this
            # neighbor, if any
            prev_cost = costs.get(next_key, None)
            # This is the cost of getting to this neighbor through the
            # current node
            next_cost = cost + weight

            # If the cost of getting here is now lower
            if prev_cost is None or next_cost < prev_cost:
                # Update the cost of getting here
                costs[next_key] = next_cost
                # We will visit this neighbor soon
                heappush(queue, (next_cost, next_key))

    # Just in case
    return -1


def aoc2023_day17_part1(lines: Iterable[str]) -> int:
    # Turn input grid into mapping between coordinates and weights
    grid = {
        (r, c): int(char)
        for r, line in enumerate(lines)
        for c, char in enumerate(line)
    }
    # The destination is the tile on the bottom-right, and thus it's the
    # "last" item in the grid
    dest_node, dest_node_cost = grid.popitem()
    grid[dest_node] = dest_node_cost

    # We will use this function to gather the valid neighbors
    def get_neighbors(
            key: PathInfo,
            dest_node: Vector,
    ) -> Iterator[tuple[int, PathInfo]]:
        node, direction, run = key
        # For each orthogonal offset
        for offset in offsets:
            # The node at this offset is a potential neighbor
            next_node = tuple(starmap(add, zip(node, offset)))
            # If neighbor is out of bounds, this neighbor is invalid
            if next_node not in grid:
                continue

            # Subtract these nodes to get the direction vector
            next_direction = tuple(starmap(sub, zip(next_node, node)))

            if direction is not None:
                # If neighbor is backwards, this neighbor is invalid
                if next_direction == tuple(map(neg, direction)):
                    continue

            turning = direction is not None and next_direction != direction
            # Calculate length of next straight run
            next_run = 1 if turning else run + 1

            # If run will be longer than 3, this neighbor is invalid
            if next_run > 3:
                continue

            yield grid[next_node], (next_node, next_direction, next_run)

    # Find the path (finally!)
    return find_path((0, 0), dest_node, get_neighbors)


def aoc2023_day17_part2(lines: Iterable[str]) -> int:
    # Turn input grid into mapping between coordinates and weights
    grid = {
        (r, c): int(char)
        for r, line in enumerate(lines)
        for c, char in enumerate(line)
    }
    # The destination is the tile on the bottom-right, and thus it's the
    # "last" item in the grid
    dest_node, dest_node_cost = grid.popitem()
    grid[dest_node] = dest_node_cost

    # We will use this function to gather the valid neighbors
    def get_neighbors(
            key: PathInfo,
            dest_node: Vector,
    ) -> Iterator[tuple[int, PathInfo]]:
        node, direction, run = key
        # For each orthogonal offset
        for offset in offsets:
            # The node at this offset is a potential neighbor
            next_node = tuple(starmap(add, zip(node, offset)))
            # If neighbor is out of bounds, this neighbor is invalid
            if next_node not in grid:
                continue

            # Subtract these nodes to get the direction vector
            next_direction = tuple(starmap(sub, zip(next_node, node)))

            if direction is not None:
                # If neighbor is backwards, this neighbor is invalid
                if next_direction == tuple(map(neg, direction)):
                    continue

            turning = direction is not None and next_direction != direction
            # Calculate length of next straight run
            next_run = 1 if turning else run + 1

            if (
                # If run will be longer than 10...
                (next_run > 10)
                # ...or we will turn before having a run of 4...
                or (turning and run < 4)
                # ...or we will reach the destination before having a
                # run of 4...
                or (next_node == dest_node and next_run < 4)
            ):
                # This neighbor is invalid
                continue

            yield grid[next_node], (next_node, next_direction, next_run)

    # Find the path (finally!)
    return find_path((0, 0), dest_node, get_neighbors)


parts = (aoc2023_day17_part1, aoc2023_day17_part2)
