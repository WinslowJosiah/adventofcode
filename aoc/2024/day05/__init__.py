from collections import defaultdict
from collections.abc import Iterable
import itertools as it


def aoc2024_day05_part1(lines: Iterable[str]) -> int:
    line_iter = iter(lines)

    rules: defaultdict[str, set[str]] = defaultdict(set)
    # Compile a set of rules until the first blank line
    for line in line_iter:
        if not line:
            break
        first_page, second_page = line.split("|")
        rules[first_page].add(second_page)

    total = 0
    # For every update in the remaining part of the input
    for line in line_iter:
        update = line.split(",")

        # If no page has a rule forcing a previous page to go after it
        # (i.e. it's in the correct order)
        if not any(
            previous_page in rules[page]
            for previous_page, page in it.combinations(update, r=2)
        ):
            # Add value of middle page
            total += int(update[len(update) // 2])

    return total


def aoc2024_day05_part2(lines: Iterable[str]) -> int:
    line_iter = iter(lines)

    rules: defaultdict[str, set[str]] = defaultdict(set)
    # Compile a set of rules until the first blank line
    for line in line_iter:
        if not line:
            break
        first_page, second_page = line.split("|")
        rules[first_page].add(second_page)

    total = 0
    # For every update in the remaining part of the input
    for line in line_iter:
        update = line.split(",")

        # If any page has a rule forcing a previous page to go after it
        # (i.e. it's not in the correct order)
        if any(
            previous_page in rules[page]
            for previous_page, page in it.combinations(update, r=2)
        ):
            # Put update in order by the rules
            # NOTE This relies on the fact that each update has a unique
            # correct order. Each page in the update has a rule saying
            # it must go before every other page in the update. This
            # means we can sort by how many of those rules there are.
            update = sorted(
                update,
                key=lambda page: len(set(rules[page]) & set(update)),
                reverse=True,
            )
            # Add value of middle page
            total += int(update[len(update) // 2])

    return total


parts = (aoc2024_day05_part1, aoc2024_day05_part2)
