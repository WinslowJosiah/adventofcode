# https://adventofcode.com/2025/day/1

from ...base import StrSplitSolution, answer


def parse_rotation(line: str) -> tuple[int, int]:
    direction = -1 if line[0] == "L" else 1
    clicks = int(line[1:])
    return direction, clicks


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 1.
    """
    _year = 2025
    _day = 1

    @answer((1172, 6932))
    def solve(self) -> tuple[int, int]:
        rotations = [parse_rotation(line) for line in self.input]
        dial = 50

        hits, passes = 0, 0
        for direction, clicks in rotations:
            # How many clicks do we need to pass the next 0?
            if direction < 0:
                clicks_to_next_zero = dial or 100
            else:
                clicks_to_next_zero = 100 - dial

            # Rotate the dial
            dial = (dial + direction * clicks) % 100

            # If the dial is exactly 0, this is a hit
            if dial == 0:
                hits += 1
            # If we pass the next 0 at least once, tally up the passes
            if clicks >= clicks_to_next_zero:
                passes += (clicks - clicks_to_next_zero) // 100 + 1

        return hits, passes
