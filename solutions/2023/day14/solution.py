# https://adventofcode.com/2023/day/14

from collections.abc import Callable, Sequence

from ...base import StrSplitSolution, answer


type Rows = tuple[Sequence[str], ...]
type Grid = tuple[str, ...]


def _roll_horizontally(
        grid: Rows,
        justify_func: Callable[[str, int, str], str],
) -> Grid:
    return tuple(
        "#".join(
            # For each section, we get only the rocks, and justify them
            # to the left or right of a string of dots
            justify_func(section.replace(".", ""), len(section), ".")
            for section in "".join(row).split("#")
        )
        for row in grid
    )


def roll_left(grid: Rows) -> Grid:
    return _roll_horizontally(grid, str.ljust)


def roll_right(grid: Rows) -> Grid:
    return _roll_horizontally(grid, str.rjust)


def roll_up(grid: Rows) -> Grid:
    return tuple(
        "".join(row)
        for row in zip(*roll_left(zip(*grid)))  # pyright: ignore[reportArgumentType]
    )


def roll_down(grid: Rows) -> Grid:
    return tuple(
        "".join(row)
        for row in zip(*roll_right(zip(*grid)))  # pyright: ignore[reportArgumentType]
    )


def get_total_load(grid: Rows) -> int:
    return sum((len(grid) - i) * row.count("O") for i, row in enumerate(grid))


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 14.
    """
    _year = 2023
    _day = 14

    @answer(102497)
    def part_1(self) -> int:
        grid = tuple(self.input)
        return get_total_load(roll_up(grid))

    @answer(105008)
    def part_2(self) -> int:
        grid = tuple(self.input)
        NUM_CYCLES = 1_000_000_000

        states: dict[tuple[str, ...], int] = {}
        for i in range(NUM_CYCLES):
            # If a loop was detected, skip to ending state and break
            if (loop_start := states.get(grid)) is not None:
                remaining = NUM_CYCLES - loop_start
                loop_length = i - loop_start
                end_i = loop_start + remaining % loop_length
                grid = next(k for k, v in states.items() if v == end_i)
                break
            # Save this state
            states[grid] = i

            grid = roll_up(grid)
            grid = roll_left(grid)
            grid = roll_down(grid)
            grid = roll_right(grid)

        return get_total_load(grid)
