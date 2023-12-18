from collections.abc import Iterable


def aoc2023_day09_part1(lines: Iterable[str]) -> int:
    from itertools import pairwise

    extra_sum = 0
    for line in lines:
        # Parse the values from the line
        diffs = list(map(int, line.split()))
        extra_val = 0
        # While the differences are not all 0
        while any(diffs):
            # Add the last difference
            extra_val += diffs[-1]
            # Find differences between these differences
            diffs = [val2 - val1 for val1, val2 in pairwise(diffs)]
        # The result will be the extrapolated value
        extra_sum += extra_val

    return extra_sum


def aoc2023_day09_part2(lines: Iterable[str]) -> int:
    from itertools import pairwise

    extra_sum = 0
    for line in lines:
        diffs = list(map(int, line.split()))

        # This is literally the only change!
        diffs.reverse()

        extra_val = 0
        while any(diffs):
            extra_val += diffs[-1]
            diffs = [val2 - val1 for val1, val2 in pairwise(diffs)]

        extra_sum += extra_val

    return extra_sum


parts = (aoc2023_day09_part1, aoc2023_day09_part2)
