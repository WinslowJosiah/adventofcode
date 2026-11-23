# https://adventofcode.com/2024/day/21

from collections.abc import Iterator
from functools import cache
from itertools import pairwise

from ...base import StrSplitSolution, answer


OFFSETS = {">": (0, 1), "<": (0, -1), "v": (1, 0), "^": (-1, 0)}


type Keypad = tuple[str, ...]
NUMERIC_KEYPAD: Keypad = ("789", "456", "123", "_0A")
DIRECTIONAL_KEYPAD: Keypad = ("_^A", "<v>")
GAP = "_"


def find_button(button: str, keypad: Keypad) -> tuple[int, int]:
    for r, row in enumerate(keypad):
        for c, char in enumerate(row):
            if char == button:
                return (r, c)
    raise RuntimeError(f"button {button} not found")


def walk(row: int, col: int, keypad: Keypad, path: str) -> Iterator[str]:
    for direction in path:
        dr, dc = OFFSETS[direction]
        row += dr
        col += dc
        yield keypad[row][col]


def paths_between(start: str, end: str, keypad: Keypad) -> list[str]:
    start_row, start_col = find_button(start, keypad)
    end_row, end_col = find_button(end, keypad)

    dr, dc = end_row - start_row, end_col - start_col
    horizontal = ">" * dc + "<" * -dc
    vertical = "v" * dr + "^" * -dr
    # NOTE Any path worth taking will consist of a horizontal section
    # and a vertical section; anything else would cause robots to move
    # unnecessarily. So we will build those two sections of the path
    # with exactly as many presses as needed, and try both orderings.
    paths = [horizontal + vertical, vertical + horizontal]

    return [
        path
        for path in paths
        if GAP not in walk(start_row, start_col, keypad, path)
    ]


@cache
def cost_between(start: str, end: str, keypad: Keypad, num_robots: int) -> int:
    # The cost between these two buttons is the lowest cost that the
    # next-higher-up controller can achieve for any robot path
    return min(
        # NOTE The next-higher-up controller presses A at the end, to
        # make the robot press the end button.
        cost(path + "A", DIRECTIONAL_KEYPAD, num_robots - 1)
        for path in paths_between(start, end, keypad)
    )


def cost(code: str, keypad: Keypad, num_robots: int) -> int:
    # If this is a human-operated keypad, the cost of any code is the
    # code's length; we can just press each button in turn
    if num_robots <= 0:
        return len(code)
    # Otherwise, the cost of this code is the total cost between all
    # pairs of buttons (starting with A, the robot's starting point)
    return sum(
        cost_between(start, end, keypad, num_robots)
        for start, end in pairwise("A" + code)
    )


def complexity(code: str, num_robots: int) -> int:
    return cost(code, NUMERIC_KEYPAD, num_robots=num_robots) * int(code[:-1])


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 21.
    """
    _year = 2024
    _day = 21

    _cached_functions = (cost_between,)

    @answer(136780)
    def part_1(self) -> int:
        return sum(complexity(code, num_robots=3) for code in self.input)

    @answer(167538833832712)
    def part_2(self) -> int:
        return sum(complexity(code, num_robots=26) for code in self.input)
