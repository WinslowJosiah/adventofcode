from collections.abc import Iterable
from typing import TypeAlias


PinHeights: TypeAlias = tuple[int, ...]


def aoc2024_day25_part1(lines: Iterable[str]) -> int:
    PIN_SPACE = 5
    line_iter = iter(lines)

    locks: list[PinHeights] = []
    keys: list[PinHeights] = []
    # Loop through the input lines
    while True:
        # Get enough rows for the pins and the top/bottom rows
        rows = [next(line_iter) for _ in range(PIN_SPACE + 2)]
        top, *middle, bottom = rows
        # Count the # characters in each column
        pin_heights = tuple(
            column.count("#")
            for column in zip(*middle)
        )

        # If the top row is filled in
        if all(c == "#" for c in top):
            # This schematic is for a lock
            locks.append(pin_heights)
        # If the bottom row is filled in
        elif all(c == "#" for c in bottom):
            # This schematic is for a key
            keys.append(pin_heights)

        # Stop looping through lines if there are no lines left
        if next(line_iter, None) is None:
            break

    # Count the number of times...
    return sum(
        # ...all the pin heights fit in the available space...
        all(l + k <= PIN_SPACE for l, k in zip(lock, key))
        # ...for every lock and key
        for lock in locks
        for key in keys
    )


def aoc2024_day25_part2(lines: Iterable[str]) -> int:
    # There is no Part 2 today! I'm free!
    return -1


parts = (aoc2024_day25_part1, aoc2024_day25_part2)
