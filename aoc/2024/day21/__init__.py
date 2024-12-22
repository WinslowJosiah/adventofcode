from collections.abc import Iterable
from functools import cache
import itertools as it
from typing import TypeAlias


Pad: TypeAlias = tuple[str, ...]
NUMPAD: Pad = ("789", "456", "123", ".0A")
DIRPAD: Pad = (".^A", "<v>")
OFFSETS = {"<": (0, -1), ">": (0, 1), "^": (-1, 0), "v": (1, 0)}


@cache
def get_button_paths(pad: Pad, button1: str, button2: str) -> list[str]:
    """
    Get all shortest paths that can be taken between two buttons on a
    keypad.
    """
    # Get locations of buttons on keypad
    (r1, c1), (r2, c2) = (
        next(
            (r, c)
            for r, row in enumerate(pad)
            for c, button in enumerate(row)
            if button == b
        )
        for b in (button1, button2)
    )
    # Get the movements along the shortest paths between the buttons
    # NOTE Every shortest path will contain the same movements, but done
    # in a different order.
    button_dr, button_dc = r2 - r1, c2 - c1
    movements = (
        "<" * -button_dc + ">" * button_dc
        + "^" * -button_dr + "v" * button_dr
    )

    paths: list[str] = []
    # For each possible ordering of the movements
    # NOTE itertools.permutations treats elements as unique based on
    # their position, not their value. Because of this, there will be
    # "duplicate" permutations to filter out.
    for sequence in set(it.permutations(movements)):
        robot_r, robot_c = r1, c1
        # Try moving the robot according to these movements
        for movement in sequence:
            robot_dr, robot_dc = OFFSETS[movement]
            robot_r += robot_dr
            robot_c += robot_dc
            # If the robot reached a gap, this path is not valid
            if pad[robot_r][robot_c] == ".":
                break
        # If nothing invalidated the path
        else:
            # This path is valid
            # NOTE An "A" should go at the end to activate this button.
            paths.append("".join(sequence) + "A")

    return paths


@cache
def get_min_sequence_length(pad: Pad, code: str, depth: int) -> int:
    """
    Get the length of the shortest sequence of button presses to enter
    the given code on the given keypad. The depth is the number of
    robots between us and the robot on the numeric keypad.
    """
    result = 0
    # For each transition between buttons, starting from the A button
    for button1, button2 in it.pairwise("A" + code):
        paths = get_button_paths(pad, button1, button2)
        # If we're controlling the numeric keypad
        if depth == 0:
            # Add the length of the shortest path
            result += min(len(path) for path in paths)
        # If we're controlling some directional keypad
        else:
            # Add the length of the shortest button sequence needed to
            # move along some path on the next keypad down
            result += min(
                get_min_sequence_length(DIRPAD, path, depth - 1)
                for path in paths
            )
    return result


def aoc2024_day21_part1(lines: Iterable[str]) -> int:
    total = 0
    for keycode in lines:
        min_sequence_length = get_min_sequence_length(
            NUMPAD, keycode,
            depth=2,
        )
        keycode_number = int("".join(c for c in keycode if c.isdigit()))
        total += min_sequence_length * keycode_number

    return total


def aoc2024_day21_part2(lines: Iterable[str]) -> int:
    total = 0
    for keycode in lines:
        min_sequence_length = get_min_sequence_length(
            NUMPAD, keycode,
            depth=25,
        )
        keycode_number = int("".join(c for c in keycode if c.isdigit()))
        total += min_sequence_length * keycode_number

    return total


parts = (aoc2024_day21_part1, aoc2024_day21_part2)
