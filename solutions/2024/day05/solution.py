# https://adventofcode.com/2024/day/5

from collections import defaultdict
from functools import cmp_to_key
from itertools import combinations

from ...base import StrSplitSolution, answer


def follows_rules(
        update: list[int], 
        predecessors: dict[int, set[int]],
) -> bool:
    return not any(
        after in predecessors[before]
        for before, after in combinations(update, 2)
    )


def middle_item(lst: list[int]) -> int:
    return lst[len(lst) // 2]


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 5.
    """
    _year = 2024
    _day = 5

    separator = "\n\n"

    @answer((5329, 5833))
    def solve(self) -> tuple[int, int]:
        raw_rules, raw_updates = (part.splitlines() for part in self.input)
        # updates will hold updates as lists of page numbers
        updates = [
            [int(u) for u in raw_update.split(",")]
            for raw_update in raw_updates
        ]
        # predecessors will map pages to pages that must go before them
        predecessors: dict[int, set[int]] = defaultdict(set)
        for raw_rule in raw_rules:
            before, after = map(int, raw_rule.split("|"))
            predecessors[after].add(before)

        def cmp_pages(a: int, b: int) -> int:
            """Old-style comparison function for page numbers."""
            # If page A comes before page B, A goes first
            if a in predecessors[b]:
                return -1
            # If page B comes before page A, B goes first
            if b in predecessors[a]:
                return 1
            # Otherwise, it doesn't matter which page goes first
            return 0

        part_1, part_2 = 0, 0
        for update in updates:
            if follows_rules(update, predecessors):
                part_1 += middle_item(update)
            else:
                sorted_update = sorted(update, key=cmp_to_key(cmp_pages))
                part_2 += middle_item(sorted_update)

        return part_1, part_2
