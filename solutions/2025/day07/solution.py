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
        # Keep track of the number of beams in each column
        beams = [0] * len(first_row)
        beams[start] = 1

        for row in last_rows:
            for col, char in enumerate(row):
                # The beam states will only change when a beam reaches a
                # splitter
                if not (char == "^" and beams[col]):
                    continue

                num_splits += 1
                # Split this column's beam to both sides
                beams[col - 1] += beams[col]
                beams[col + 1] += beams[col]
                # No beam will continue in this column
                # HACK This overwrites beams in the case of two adjacent
                # splitters, but that never happens in the input.
                beams[col] = 0

        return num_splits, sum(beams)
