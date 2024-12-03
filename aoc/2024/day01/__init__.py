from collections.abc import Iterable


def aoc2024_day01_part1(lines: Iterable[str]) -> int:
    # Parse lists
    left_list: list[int]
    right_list: list[int]
    left_list, right_list = zip(*[
        map(int, line.split())
        for line in lines
    ])

    # Total distance is the sum of...
    return sum(
        # ...the absolute difference between the values...
        abs(left_item - right_item)
        # ...of the pairs of items in each list, when they're sorted
        for left_item, right_item in zip(
            sorted(left_list), sorted(right_list),
        )
    )


def aoc2024_day01_part2(lines: Iterable[str]) -> int:
    from collections import Counter

    # Parse lists
    left_list: list[int]
    right_list: list[int]
    left_list, right_list = zip(*[
        map(int, line.split())
        for line in lines
    ])

    right_counter = Counter(right_list)
    # Similarity score is the sum of...
    return sum(
        # ...each item in the left list, times its frequency in the
        # right list
        item * right_counter[item]
        for item in left_list
    )


parts = (aoc2024_day01_part1, aoc2024_day01_part2)
