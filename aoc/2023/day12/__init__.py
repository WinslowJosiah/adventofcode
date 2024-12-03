from collections.abc import Iterable
from functools import cache


def count_arrangements(springs: str, groups: list[int]) -> int:
    """
    Count the number of valid arrangements for a row of springs with
    group lengths of `groups`.
    """
    # NOTE: To count the arrangements effectively, we use something
    # called "dynamic programming". Dynamic programming involves
    # recursion (solving a problem based on smaller instances of the
    # same problem) and caching (saving earlier results to avoid
    # re-computing them later).
    @cache
    def helper(
            i: int = 0,
            g: int = 0,
            m: int = sum(groups) + len(groups) - 1,
    ) -> int:
        # If all groups have been considered
        if g >= len(groups):
            # If there are no more pre-filled groups on the row
            if springs.find("#", i) < 0:
                # This is a valid solution
                return 1
            else:
                # Otherwise, there are no valid solutions
                return 0

        # Number of valid solutions so far
        result = 0
        # Number of groups left to process
        group_count = len(groups) - g
        # Number of cells that aren't in a group or a separator
        # between groups
        empty_cells = len(springs) - i - m
        # For each possible number of "."s before the last groups
        for run_length in range(group_count + empty_cells):
            # These cells would be next
            next_cells = ("." * run_length) + ("#" * groups[g]) + "."

            springs_iter = iter(springs[j] for j in range(i, len(springs)))
            valid = True
            # Check that each cell is compatible with the original
            # row of cells
            for char, orig_char in zip(next_cells, springs_iter):
                if orig_char == "?":
                    continue
                if orig_char != char:
                    valid = False
                    break
            if not valid:
                continue

            # If we're still here, this run of "."s is valid
            # Find the number of solutions for the rest of the row
            result += helper(
                i + run_length + groups[g] + 1,
                g + 1,
                m - groups[g] - 1,
            )

        return result

    # Recursion is fun /s
    return helper()


def aoc2023_day12_part1(lines: Iterable[str]) -> int:
    arrangement_sum = 0
    for line in lines:
        # Extract the row of springs and groups from the line
        springs, groups_str = line.split()
        groups = list(map(int, groups_str.split(",")))
        # Count the possible arrangements of springs
        arrangement_sum += count_arrangements(springs, groups)

    return arrangement_sum


def aoc2023_day12_part2(lines: Iterable[str]) -> int:
    arrangement_sum = 0
    for line in lines:
        springs, groups_str = line.split()
        groups = list(map(int, groups_str.split(",")))

        # This is literally the only change!
        springs = "?".join([springs] * 5)
        groups *= 5

        arrangement_sum += count_arrangements(springs, groups)

    return arrangement_sum


parts = (aoc2023_day12_part1, aoc2023_day12_part2)
