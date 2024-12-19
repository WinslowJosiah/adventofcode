from collections.abc import Iterable
from functools import cache


def aoc2024_day19_part1(lines: Iterable[str]) -> int:
    line_iter = iter(lines)
    # Towels are in the first line of the input...
    towels = next(line_iter).split(", ")
    # ...followed by a blank line
    next(line_iter)

    @cache
    def validate_design(design: str) -> bool:
        # You can always arrange towels into no design
        if not design:
            return True
        return any(
            # Check that the rest of the design is valid...
            validate_design(design.removeprefix(towel))
            # ...for each towel that can go at the start
            for towel in towels
            if design.startswith(towel)
        )

    # The rest of the input is the list of designs
    # NOTE Python treats True as 1 and False as 0 in numeric contexts.
    return sum(
        validate_design(design)
        for design in line_iter
    )


def aoc2024_day19_part2(lines: Iterable[str]) -> int:
    line_iter = iter(lines)
    # Towels are in the first line of the input...
    towels = next(line_iter).split(", ")
    # ...followed by a blank line
    next(line_iter)

    @cache
    def count_towel_arrangements(design: str) -> int:
        # There is only one way to arrange towels into no design
        if not design:
            return 1
        return sum(
            # Count the possible towel arrangements for the rest of the
            # design...
            count_towel_arrangements(design.removeprefix(towel))
            # ...for each towel that can go at the start
            for towel in towels
            if design.startswith(towel)
        )

    # The rest of the input is the list of designs
    return sum(
        count_towel_arrangements(design)
        for design in line_iter
    )


parts = (aoc2024_day19_part1, aoc2024_day19_part2)
