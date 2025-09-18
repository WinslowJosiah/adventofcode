# https://adventofcode.com/2023/day/8

from itertools import cycle
from math import lcm
import re

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 8.
    """
    _year = 2023
    _day = 8

    separator = "\n\n"

    def _parse_input(self) -> tuple[cycle[str], dict[str, dict[str, str]]]:
        raw_turns, raw_nodes = self.input
        turns = cycle(raw_turns)
        nodes: dict[str, dict[str, str]] = {}
        for line in raw_nodes.splitlines():
            root, l, r = re.findall(r"\w+", line)
            nodes[root] = {"L": l, "R": r}
        return turns, nodes

    def _solve(self, current: str) -> int:
        turns, nodes = self._parse_input()
        for turn_index, turn in enumerate(turns):
            if current.endswith("Z"):
                return turn_index
            current = nodes[current][turn]
        # NOTE The loop is infinite unless the path ends, so this is
        # never reached. But the type checker doesn't know that.
        assert False

    @answer(18673)
    def part_1(self) -> int:
        return self._solve("AAA")

    @answer(17972669116327)
    def part_2(self) -> int:
        _, nodes = self._parse_input()
        # NOTE Each start node acts like a fixed-length oscillator with
        # its unique destination node; the point at which all
        # destination nodes are reached simultaneously is the LCM of all
        # the path lengths.
        return lcm(*[self._solve(n) for n in nodes if n.endswith("A")])
