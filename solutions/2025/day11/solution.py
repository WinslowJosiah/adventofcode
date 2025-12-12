# https://adventofcode.com/2025/day/11

from collections.abc import Iterable
from functools import cache

from ...base import StrSplitSolution, answer


def create_graph(lines: list[str]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for line in lines:
        device, outputs = line.split(": ")
        graph[device] = outputs.split()
    return graph


def num_paths(
        graph: dict[str, list[str]],
        start: str,
        end: str,
        middle: Iterable[str] | None = None,
) -> int:
    middle_set = frozenset(middle if middle is not None else ())

    @cache
    def _num_paths(node: str, seen: frozenset[str]) -> int:
        if node == end:
            # Path is only valid if we've seen every "middle" device
            return 1 if seen == middle_set else 0

        new_seen = seen
        if node in middle_set:
            new_seen = seen | {node}
        return sum(
            _num_paths(next_node, new_seen)
            for next_node in graph.get(node, [])
        )

    return _num_paths(start, frozenset[str]())


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 11.
    """
    _year = 2025
    _day = 11

    @answer(782)
    def part_1(self) -> int:
        graph = create_graph(self.input)
        return num_paths(graph, "you", "out")

    @answer(401398751986160)
    def part_2(self) -> int:
        ...
        graph = create_graph(self.input)
        return num_paths(graph, "svr", "out", middle=["dac", "fft"])
