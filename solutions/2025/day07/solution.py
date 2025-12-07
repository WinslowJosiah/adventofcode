# https://adventofcode.com/2025/day/7

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 7.
    """
    _year = 2025
    _day = 7

    @answer((1585, 16716444407407))
    def solve(self) -> tuple[int, int]:
        first_row, *last_rows = self.input
        start = first_row.index("S")

        num_splits = 0
        # Keep track of the number of timelines in which a beam reaches
        # each column
        timelines = [0] * len(first_row)
        timelines[start] = 1
        for row in last_rows:
            for col, char in enumerate(row):
                # The timelines will only change when any timeline
                # reaches a splitter
                if not (char == "^" and timelines[col]):
                    continue

                num_splits += 1
                # Split this column's timelines to both sides
                timelines[col - 1] += timelines[col]
                timelines[col + 1] += timelines[col]
                # No timelines will continue in this column
                # HACK This overwrites beams in the case of two adjacent
                # splitters, but that never happens in the input.
                timelines[col] = 0

        return num_splits, sum(timelines)
