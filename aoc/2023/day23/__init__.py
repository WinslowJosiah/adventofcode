from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from itertools import starmap
from operator import add


type Vector = tuple[int, ...]


# The valid offsets from each type of tile 
directions: dict[str, list[Vector]] = {
    "^": [(-1, 0)],
    "v": [(1, 0)],
    "<": [(0, -1)],
    ">": [(0, 1)],
    ".": [(-1, 0), (0, -1), (0, 1), (1, 0)],
}


def create_graph(
        grid: list[str],
        neighbors: Callable[[Vector, list[str]], Iterable[Vector]],
        *intersection_nodes: Vector,
) -> defaultdict[Vector, dict[Vector, int]]:
    """
    Create a graph from a grid of tiles. The graph stores the distances
    between each pair of "intersections".

    `neighbors` is a function that takes a node and a grid of tiles, and
    yields the nodes that are valid neighbors to the input node.
    """
    height = len(grid)
    width = len(grid[0])
    # A tile is an intersection if it has 3 or more neighbors, or if
    # it's specified as an "intersection"
    intersections: set[Vector] = set(
        (row, col)
        for row in range(height)
        for col in range(width)
        if len(list(neighbors((row, col), grid))) >= 3
    ) | set(intersection_nodes)

    graph: defaultdict[Vector, dict[Vector, int]] = defaultdict(dict)
    # For each intersection node
    for intersection in intersections:
        # We will travel outwards in all directions, keeping track of
        # the current node and cost incurred so far
        stack: list[tuple[Vector, int]] = [(intersection, 0)]
        visited: set[Vector] = set([intersection])
        # While there are nodes left to explore
        while stack:
            node, cost = stack.pop()
            # If this node is an intersection (and not the same one we
            # started with)
            if cost > 0 and node in intersections:
                # Save the cost of travelling to this node
                graph[intersection][node] = cost
                continue

            cost += 1
            # For each neighbor of this node
            for neighbor in neighbors(node, grid):
                if neighbor in visited:
                    continue
                # This neighbor shall be explored
                stack.append((neighbor, cost))
                visited.add(neighbor)

    return graph


def find_longest_path(
        graph: Mapping[Vector, dict[Vector, int]],
        src_node: Vector,
        dest_node: Vector,
) -> int:
    """
    Find the path from `src_node` to `dest_node` incurring the highest
    cost.
    """
    # OPTIMIZE: The current algorithm is an exhaustive depth-first
    # search of every path from src_node to dest_node. I'm aware of a
    # much better algorithm for directed acyclic graphs (which works for
    # Part 1), but I'm unaware of a better algorithm for Part 2.
    visited: set[Vector] = set()
    def helper(node: Vector) -> int | None:
        if node == dest_node:
            return 0

        max_cost = None
        visited.add(node)
        for next_node, next_cost in graph[node].items():
            if next_node in visited:
                continue

            remaining_cost = helper(next_node)
            if remaining_cost is None:
                continue
            cost = remaining_cost + next_cost
            if max_cost is None or cost > max_cost:
                max_cost = cost
        visited.remove(node)

        return max_cost

    result = helper(src_node)
    assert result is not None
    return result


def aoc2023_day23_part1(lines: Iterable[str]) -> int:
    def get_neighbors(node: Vector, grid: list[str]) -> Iterable[Vector]:
        row, col = node
        # NOTE: In Part 1, the valid neighbors depend on which tile
        # you're on. If it's a slope, only one direction is valid.
        try:
            tile = grid[row][col]
        except IndexError:
            return

        for offset in directions.get(tile, []):
            next_node: Vector = tuple(starmap(add, zip(node, offset)))
            row, col = next_node

            try:
                tile = grid[row][col]
            except IndexError:
                continue

            if tile == "#":
                continue
            yield next_node

    grid = list(lines)
    src_node = (0, grid[0].index("."))
    dest_node = (len(grid) - 1, grid[-1].index("."))

    graph = create_graph(grid, get_neighbors, src_node, dest_node)
    return find_longest_path(graph, src_node, dest_node)


def aoc2023_day23_part2(lines: Iterable[str]) -> int:
    def get_neighbors(node: Vector, grid: list[str]) -> Iterable[Vector]:
        # NOTE: In Part 2, the slope tiles are ignored, and treated as
        # path tiles.
        for offset in directions["."]:
            next_node: Vector = tuple(starmap(add, zip(node, offset)))
            row, col = next_node

            try:
                tile = grid[row][col]
            except IndexError:
                continue

            if tile == "#":
                continue
            yield next_node

    grid = list(lines)
    src_node = (0, grid[0].index("."))
    dest_node = (len(grid) - 1, grid[-1].index("."))

    graph = create_graph(grid, get_neighbors, src_node, dest_node)
    return find_longest_path(graph, src_node, dest_node)


parts = (aoc2023_day23_part1, aoc2023_day23_part2)
