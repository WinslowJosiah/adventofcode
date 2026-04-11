# https://adventofcode.com/2024/day/1

from collections import Counter

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 1.
    """
    _year = 2024
    _day = 1

    @answer((1341714, 27384707))
    def solve(self) -> tuple[int, int]:
        pairs = [tuple(int(n) for n in line.split()) for line in self.input]
        left, right = [sorted(values) for values in zip(*pairs)]

        total_distance = sum(abs(l - r) for l, r in zip(left, right))

        right_counts = Counter(right)
        similarity_score = sum(l * right_counts[l] for l in left)

        return total_distance, similarity_score
