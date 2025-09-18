# https://adventofcode.com/2023/day/13

from collections.abc import Sequence

from ...base import StrSplitSolution, answer


def num_smudges(a: Sequence[str], b: Sequence[str]) -> int:
    return sum(char_a != char_b for char_a, char_b in zip(a, b))


def find_mirror_row(rows: Sequence[Sequence[str]], smudges: int) -> int:
    # NOTE Row 0 is not included, because the rows above would be empty,
    # and we'd detect this as a valid reflection. We don't want that.
    for i in range(1, len(rows)):
        above, below = rows[:i], rows[i:]
        if (
            sum(num_smudges(a, b) for a, b in zip(reversed(above), below))
            == smudges
        ):
            return i
    return 0


def score_block(block: str, smudges: int = 0) -> int:
    rows = block.splitlines()
    if row := find_mirror_row(rows, smudges):
        return 100 * row
    if col := find_mirror_row(list(zip(*rows)), smudges):
        return col
    return 0


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 13.
    """
    _year = 2023
    _day = 13

    separator = "\n\n"

    @answer(30158)
    def part_1(self) -> int:
        return sum(score_block(block) for block in self.input)

    @answer(36474)
    def part_2(self) -> int:
        return sum(score_block(block, smudges=1) for block in self.input)
