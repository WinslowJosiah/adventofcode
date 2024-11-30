from collections.abc import Iterable


def aoc2023_day04_part1(lines: Iterable[str]) -> int:
    import re

    # This regex will match cards, and group the lists of numbers
    card_regex = re.compile(r"Card [\d\s]+: ([\d\s]+)\|([\d\s]+)")

    points = 0
    for line in lines:
        # Extract winning numbers and card numbers from card
        re_match = card_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        winning_nums_str, card_nums_str = re_match.groups()
        # NOTE: I don't need to treat the numbers as integers, so I'm
        # not converting them to integers.
        # Also, I make them into sets, and not lists, because you can
        # quickly check the values in common between two sets using &.
        winning_nums = set(winning_nums_str.split())
        card_nums = set(card_nums_str.split())

        # Count numbers that are members of both sets
        match_count = len(winning_nums & card_nums)
        # If there is more than one match
        if match_count > 0:
            # Add the correct number of points to the total
            # (Powers of 2 are neat!)
            points += 2 ** (match_count - 1)

    return points


def aoc2023_day04_part2(lines: Iterable[str]) -> int:
    from collections import defaultdict
    import re

    # This regex will match cards, and group the lists of numbers
    card_regex = re.compile(r"Card [\d\s]+: ([\d\s]+)\|([\d\s]+)")

    # In this defaultdict, the keys are card indices, and the values are
    # how many copies of that scratchcard I have
    scratchcard_counts: defaultdict[int, int] = defaultdict(int)

    for card_i, line in enumerate(lines):
        # I now have this scratchcard
        scratchcard_counts[card_i] += 1

        # Extract winning numbers and card numbers from card
        re_match = card_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        winning_nums_str, card_nums_str = re_match.groups()
        winning_nums = set(winning_nums_str.split())
        card_nums = set(card_nums_str.split())

        # Count numbers that are members of both sets
        match_count = len(winning_nums & card_nums)
        # I win more scratchcards depending on how many matches I have
        for j in range(match_count):
            # The number of scratchcards I win is however many of the
            # current scratchcard I have, because I win in each of them
            scratchcard_counts[card_i + j + 1] += scratchcard_counts[card_i]

    # Sum together the number of scratchcards you've won
    return sum(scratchcard_counts.values())


parts = (aoc2023_day04_part1, aoc2023_day04_part2)
