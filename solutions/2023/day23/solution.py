# https://adventofcode.com/2023/day/23

from collections import defaultdict

from ...base import StrSplitSolution, answer, slow
from ...utils.grids import (
    Direction, Grid, GridPoint, add_points, neighbors, parse_grid,
)


SLOPES = {
    ">": Direction.RIGHT,
    "v": Direction.DOWN,
    "<": Direction.LEFT,
    "^": Direction.UP,
}


type Graph = dict[GridPoint, dict[GridPoint, int]]


def get_moves_from(
        grid: Grid[str],
        point: GridPoint,
        with_slopes: bool,
) -> list[GridPoint]:
    # If we are following slopes and there is a slope here
    if with_slopes and (slope := SLOPES.get(grid[point])):
        # Move along the slope
        moves = [add_points(point, slope.offset)]
    else:
        # Otherwise, move in all directions
        moves = list(neighbors(point, num_directions=4))

    return [m for m in moves if m in grid]


def create_graph(
        grid: Grid[str],
        start: GridPoint,
        end: GridPoint,
        with_slopes: bool,
) -> Graph:
    # Gather all "intersections" (including the start and end nodes)
    intersections = {start, end} | {
        point
        for point in grid
        if len(get_moves_from(grid, point, with_slopes)) > 2
    }

    graph: Graph = defaultdict(dict)
    for intersection in intersections:
        for initial_move in get_moves_from(grid, intersection, with_slopes):
            if initial_move not in grid:
                continue

            # Start at this intersection; move in the initial direction
            previous, current = intersection, initial_move
            distance = 1
            while current not in intersections:
                # Get moves from here without doubling back
                moves = [
                    m
                    for m in get_moves_from(grid, current, with_slopes)
                    if m != previous
                ]
                # If there are no moves, we've hit a dead end
                if not moves:
                    break
                # NOTE The paths between intersections should be long
                # "hallways" with one path forward.
                assert len(moves) == 1, f"unexpected intersection at {current}"

                previous, current = current, moves[0]
                distance += 1
            else:
                # If we haven't hit a dead end, record the distance
                graph[intersection][current] = distance

    return graph


def find_longest_path(
        graph: Graph,
        start: GridPoint,
        end: GridPoint,
) -> int:
    max_distance = 0
    seen: set[GridPoint] = set()

    # NOTE This is a naive depth-first search. In Part 1, the graph is a
    # DAG, so there is a better longest-path algorithm; for Part 2,
    # however, there is no asymptotically better algorithm than this.
    def search(node: GridPoint, distance: int):
        nonlocal max_distance
        if node == end:
            max_distance = max(max_distance, distance)
            return

        seen.add(node)
        for neighbor, distance_to_neighbor in graph[node].items():
            if neighbor not in seen:
                search(neighbor, distance + distance_to_neighbor)
        seen.remove(node)

    search(start, 0)
    return max_distance


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 23.
    """
    _year = 2023
    _day = 23

    def _solve(self, with_slopes: bool) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        start, end = min(grid.keys()), max(grid.keys())

        graph = create_graph(grid, start, end, with_slopes=with_slopes)
        return find_longest_path(graph, start, end)

    @answer(1930)
    def part_1(self) -> int:
        return self._solve(with_slopes=True)

    @answer(6230)
    @slow
    def part_2(self) -> int:
        return self._solve(with_slopes=False)
