from collections.abc import Iterable, Iterator
import re
from typing import cast, TypeAlias


XYPair: TypeAlias = tuple[int, int]
Machine: TypeAlias = tuple[XYPair, XYPair, XYPair]


def iter_machines(lines: Iterable[str]) -> Iterator[Machine]:
    """
    Iterate through each claw machine in the input.
    """
    numbers_regex = re.compile(r"(\d+).+?(\d+)")

    line_iter = iter(lines)
    while True:
        machine: list[XYPair] = []
        # Get the numbers from the Button A, Button B, and Prize lines
        for _ in range(3):
            match = numbers_regex.search(next(line_iter))
            assert match is not None
            machine.append(cast(XYPair, tuple(map(int, match.groups()))))

        yield cast(Machine, tuple(machine))
        # Stop if there are no more lines
        if next(line_iter, None) is None:
            return


def solve_machine(machine: Machine) -> tuple[int, int] | None:
    """
    Solve for the number of A presses and B presses needed to win the
    prize on this claw machine.

    If there are no integer solutions, `None` is returned.
    """
    (ax, ay), (bx, by), (px, py) = machine

    # Calculate A presses via elimination
    a_presses, remainder = divmod(px * by - py * bx, ax * by - ay * bx)
    # If A presses isn't an integer, there is no integer solution
    if remainder:
        return None

    # Calculate B presses with X equation
    b_presses, remainder = divmod(px - ax * a_presses, bx)
    # If B presses isn't an integer, there is no integer solution
    if remainder:
        return None

    # Sanity check
    assert ax * a_presses + bx * b_presses == px
    assert ay * a_presses + by * b_presses == py
    # We've found an integer solution
    return (a_presses, b_presses)


def aoc2024_day13_part1(lines: Iterable[str]) -> int:
    cost = 0
    for machine in iter_machines(lines):
        if (solution := solve_machine(machine)) is not None:
            a_presses, b_presses = solution
            cost += 3 * a_presses + b_presses

    return cost


def aoc2024_day13_part2(lines: Iterable[str]) -> int:
    cost = 0
    for a, b, (px, py) in iter_machines(lines):
        # Whoops, we're somehow off by 10 trillion
        px += 10_000_000_000_000
        py += 10_000_000_000_000

        if (solution := solve_machine((a, b, (px, py)))) is not None:
            a_presses, b_presses = solution
            cost += 3 * a_presses + b_presses

    return cost


parts = (aoc2024_day13_part1, aoc2024_day13_part2)
