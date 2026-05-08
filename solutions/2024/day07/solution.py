# https://adventofcode.com/2024/day/7

from ...base import StrSplitSolution, answer


def process_line(line: str, include_concat: bool = False) -> int:
    target, *numbers = map(int, line.replace(":", "").split())
    if is_solvable(numbers, target, include_concat):
        return target
    return 0


def is_solvable(
        numbers: list[int],
        target: int,
        include_concat: bool = False,
) -> bool:
    # Base case: there is only one number, so is it the target?
    if len(numbers) == 1:
        return numbers[0] == target

    *rest, last = numbers

    if include_concat:
        # Can the target be the result of a concat?
        str_last, str_target = str(last), str(target)
        if str_target.endswith(str_last):
            prefix = str_target.removesuffix(str_last)
            # NOTE We cannot concat with an empty prefix!
            if prefix and is_solvable(rest, int(prefix), include_concat):
                return True

    # Can the target be the result of a multiplication?
    quotient, remainder = divmod(target, last)
    if remainder == 0:
        if is_solvable(rest, quotient, include_concat):
            return True

    # Can the target be the result of an addition?
    difference = target - last
    if difference > 0:
        if is_solvable(rest, difference, include_concat):
            return True

    # If we're here, the answer is no
    return False


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 7.
    """
    _year = 2024
    _day = 7

    @answer(465126289353)
    def part_1(self) -> int:
        return sum(process_line(line) for line in self.input)

    @answer(70597497486371)
    def part_2(self) -> int:
        return sum(
            process_line(line, include_concat=True)
            for line in self.input
        )
