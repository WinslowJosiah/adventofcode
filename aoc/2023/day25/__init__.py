from collections.abc import Iterable


def aoc2023_day25_part1(lines: Iterable[str]) -> int:
    import networkx as nx

    # Build the graph of connected components
    graph = nx.Graph()
    for line in lines:
        left, right = line.split(": ")
        for node in right.split():
            graph.add_edge(left, node)  # type: ignore

    # NOTE: NetworkX is doing most of the heavy lifting here.
    graph.remove_edges_from(nx.minimum_edge_cut(graph))  # type: ignore
    group1, group2 = nx.connected_components(graph)  # type: ignore

    return len(group1) * len(group2)  # type: ignore


def aoc2023_day25_part2(lines: Iterable[str]) -> int:
    # There is no Part 2 today! I'm free!
    return -1


parts = (aoc2023_day25_part1, aoc2023_day25_part2)
