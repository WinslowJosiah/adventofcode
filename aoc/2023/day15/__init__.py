from collections.abc import Iterable
from functools import reduce


def holiday_hash(s: str):
    """
    Compute the result of the HASH (Holiday ASCII String Helper)
    algorithm applied to the given string.

    The algorithm works by doing the following for each character in the
    string, starting with a current value of 0:

    - Add the ASCII value of the character to the current value.
    - Multiply the current value by 17.
    - Set the current value to itself modulo 256.

    After every character in the string has been processed, the current
    value is the output of the algorithm.
    """
    # Thanks to functools.reduce, this can be a single statement!
    return reduce(
        lambda a, b: ((a + ord(b)) * 17) % 256,
        s, 0
    )


def aoc2023_day15_part1(lines: Iterable[str]) -> int:
    # The input is in the form of a single line
    line = next(iter(lines))
    # Sum the HASHes of each string
    return sum(map(holiday_hash, line.split(",")))


def aoc2023_day15_part2(lines: Iterable[str]) -> int:
    from collections import defaultdict
    import re

    # This regex matches commands, and groups the lens label and focal
    # length (the absence of a focal length means this is a - command)
    command_regex = re.compile(r"(\w+)(?:-|=(\d+))")
    # This will help us perform our Holiday ASCII String Helper Manual
    # Arrangement Procedure (HASHMAP)
    # NOTE: The specs suggest we should be storing our boxes as lists of
    # tuples of strings and ints. While this is extremely close to how
    # hashmaps work under the hood, it's more convenient in this case to
    # exploit the properties of Python's dict type (constant-time insert
    # and remove, and remembering insertion order).
    holiday_hashmap: defaultdict[int, dict[str, int]] = defaultdict(dict)

    # The input is in the form of a single line
    line = next(iter(lines))
    # For each command in the input
    for command in line.split(","):
        # HACK: Any more sane system would parse the commands with
        # something other than regex, and they'd do it in some other way
        # than this.
        re_match = command_regex.fullmatch(command)
        assert re_match is not None  # This makes the type checker happy
        label, focal_length = re_match.groups()

        label_hash = holiday_hash(label)
        # If a focal length was provided
        if focal_length is not None:
            # This is a = command
            # Place this lens in the HASHMAP
            holiday_hashmap[label_hash][label] = int(focal_length)
        # If a focal length was not provided
        else:
            # This is a - command
            # Remove this lens from the HASHMAP
            holiday_hashmap[label_hash].pop(label, None)

    # The focusing power is the sum of...
    return sum(
        sum(
            # ...the 1-based box index, times the 1-based lens index,
            # times the focal length of this lens...
            (box_i + 1) * lens_i * focal_length
            # ...for every lens in the box...
            for lens_i, focal_length in enumerate(box.values(), 1)
        )
        # ...for every box in the HASHMAP
        for box_i, box in holiday_hashmap.items()
    )


parts = (aoc2023_day15_part1, aoc2023_day15_part2)
