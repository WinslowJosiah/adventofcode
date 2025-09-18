# https://adventofcode.com/2023/day/15

from collections import defaultdict

from ...base import StrSplitSolution, answer


def holiday_hash(st: str) -> int:
    result = 0
    for c in st:
        result += ord(c)
        result *= 17
        result %= 256
    return result


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 15.
    """
    _year = 2023
    _day = 15

    separator = ","

    @answer(506437)
    def part_1(self) -> int:
        return sum(map(holiday_hash, self.input))

    @answer(288521)
    def part_2(self) -> int:
        boxes: dict[int, dict[str, int]] = defaultdict(dict)
        for step in self.input:
            # If step looks like "abc-"
            if "-" in step:
                label = step[:-1]
                boxes[holiday_hash(label)].pop(label, None)
            # If step looks like "abc=6"
            elif "=" in step:
                label, val_str = step.split("=")
                boxes[holiday_hash(label)][label] = int(val_str)
            else:
                raise ValueError(f"unrecognized step: {step}")

        return sum(
            (box_id + 1) * (lens_pos + 1) * focal_length
            for box_id, box in boxes.items()
            for lens_pos, focal_length in enumerate(box.values())
        )
