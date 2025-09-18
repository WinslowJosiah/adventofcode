# https://adventofcode.com/2023/day/12

from functools import cache

from ...base import StrSplitSolution, answer


@cache
def num_solutions(record: str, groups: tuple[int, ...]) -> int:
    # If there are no groups
    if not groups:
        # No solutions if there are unaccounted-for `#`s in the record;
        # one solution if there aren't (where every `?` is a `.`)
        return 0 if "#" in record else 1
    # There are groups; no solutions if they can't possibly fit in the
    # rest of the record
    # if sum(groups) + len(groups) - 1 > len(record):
    if not record:
        return 0

    char, rest = record[0], record[1:]
    if char == ".":
        # Find solutions going through rest of records
        return num_solutions(rest, groups)
    elif char == "#":
        group = groups[0]
        # No solutions if the record isn't long enough for this group
        if len(record) < group:
            return 0
        # No solutions if any `.`s are in this group
        if "." in record[:group]:
            return 0
        # No solutions if a `#` is just after this group (which would
        # make the group bigger)
        if len(record) > group and record[group] == "#":
            return 0
        # Find solutions after removing this group
        return num_solutions(record[group + 1 :], groups[1:])
    else:
        # Find solutions after substituting either character
        return (
            num_solutions("#" + rest, groups)
            + num_solutions("." + rest, groups)
        )


def solve_line(line: str, with_multiplier: bool = False) -> int:
    record, raw_shape = line.split()
    groups = tuple(map(int, raw_shape.split(",")))
    if with_multiplier:
        record = "?".join([record] * 5)
        groups *= 5
    return num_solutions(record, groups)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 12.
    """
    _year = 2023
    _day = 12
    _cached_functions = (num_solutions,)

    @answer(7307)
    def part_1(self) -> int:
        return sum(solve_line(line) for line in self.input)

    @answer(3415570893842)
    def part_2(self) -> int:
        return sum(
            solve_line(line, with_multiplier=True)
            for line in self.input
        )
