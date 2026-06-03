# https://adventofcode.com/2024/day/13

from fractions import Fraction
import re

from ...base import StrSplitSolution, answer


def solve_machine(
        ax: int, ay: int, bx: int, by: int, prize_x: int, prize_y: int,
) -> tuple[Fraction, Fraction]:
    # NOTE The X/Y position of the claw after the A and B presses can be
    # modeled as linear equations. We can solve these equations for the
    # number of A and B presses using some algebra.
    denominator = ax * by - ay * bx
    a_presses = Fraction(-bx * prize_y + by * prize_x, denominator)
    b_presses = Fraction( ax * prize_y - ay * prize_x, denominator)
    return a_presses, b_presses


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 13.
    """
    _year = 2024
    _day = 13

    separator = "\n\n"

    def _solve(self, prize_offset: int = 0) -> int:
        total = 0
        for block in self.input:
            machine = [int(m) for m in re.findall(r"\d+", block)]
            # Add offset to prize position
            machine[4] += prize_offset
            machine[5] += prize_offset

            a, b = solve_machine(*machine)
            # "An A press is an A press; you can't say it's only a half"
            if a.is_integer() and b.is_integer():
                total += 3 * a + b

        return int(total)

    @answer(39996)
    def part_1(self) -> int:
        return self._solve()

    @answer(73267584326867)
    def part_2(self) -> int:
        return self._solve(prize_offset=10_000_000_000_000)
