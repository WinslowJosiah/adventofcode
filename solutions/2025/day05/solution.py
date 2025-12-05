# https://adventofcode.com/2025/day/5

from operator import attrgetter

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 5.
    """
    _year = 2025
    _day = 5

    separator = "\n\n"

    def _parse_input(self) -> tuple[list[range], list[int]]:
        raw_ranges, raw_ids = map(str.splitlines, self.input)

        ranges: list[range] = []
        for raw_range in raw_ranges:
            start, stop = map(int, raw_range.split("-"))
            # NOTE The stop of the range is inclusive.
            ranges.append(range(start, stop + 1))
        ids = [int(_id) for _id in raw_ids]
        return ranges, ids

    @answer(739)
    def part_1(self) -> int:
        ranges, ids = self._parse_input()
        return sum(1 for _id in ids if any(_id in r for r in ranges))

    @answer(344486348901788)
    def part_2(self) -> int:
        ranges, _ = self._parse_input()

        merged_ranges: list[range] = []
        # Loop through ranges in ascending order
        for right in sorted(ranges, key=attrgetter("start")):
            # If there is no left range to merge with, or the ranges
            # don't overlap, append the right range as-is
            if (
                not merged_ranges
                or (left := merged_ranges[-1]).stop < right.start
            ):
                merged_ranges.append(right)
            # Otherwise, merge and replace the left range
            else:
                merged_ranges[-1] = range(
                    min(left.start, right.start),
                    max(left.stop, right.stop),
                )

        # NOTE By now, none of the ranges should be overlapping, so
        # their lengths can now be totaled directly.
        return sum(len(r) for r in merged_ranges)
