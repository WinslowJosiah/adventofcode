# https://adventofcode.com/2023/day/25

from collections import defaultdict
from copy import deepcopy
from math import prod
import random
from typing import Hashable

from ...base import StrSplitSolution, answer


type Node = Hashable
type Graph[N: Node] = dict[N, list[N]]


def karger_minimum_cut[N: Node](graph: Graph[N]) -> tuple[int, list[int]]:
    """
    Calculate a minimum cut for a graph.

    This function uses a randomized algorithm; it is not guaranteed to
    return a minimum cut. However, if it is repeated, a minimum cut will
    be found with high probability.

    Parameters
    ----------
    graph: dict of {node : list of node}
        Graph to calculate a minimum cut for.

    Returns
    -------
    tuple of (int, list of int)
        The number of edges in the cut, and the resulting sizes of each
        connected group.
    """
    adjacency = deepcopy(graph)
    group_sizes = {node: 1 for node in graph}

    # Until there are two groups of contracted nodes
    while len(adjacency) > 2:
        # Choose random edge, with endpoints u and v
        # HACK This doesn't select edges with equal probability as would
        # be ideal, but it's short, and it works well enough.
        u, u_neighbors = random.choice(list(adjacency.items()))
        v = random.choice(u_neighbors)

        # Contract v into u
        adjacency[u].extend(adjacency[v])
        for node in adjacency[v]:
            adjacency[node].remove(v)
            adjacency[node].append(u)
        group_sizes[u] += group_sizes[v]
        # Remove self-loops from u
        adjacency[u] = [node for node in adjacency[u] if node != u]
        # Remove v
        del adjacency[v]
        del group_sizes[v]

    return len(next(iter(adjacency.values()))), list(group_sizes.values())


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 25.
    """
    _year = 2023
    _day = 25

    @answer(572000)
    def part_1(self) -> int:
        graph: Graph[str] = defaultdict(list)
        for line in self.input:
            root, nodes = line.split(": ")
            for node in nodes.split():
                graph[root].append(node)
                graph[node].append(root)

        while True:
            num_edges, group_sizes = karger_minimum_cut(graph)
            if num_edges <= 3:
                return prod(group_sizes)
