# https://adventofcode.com/2024/day/17

from collections.abc import Iterator
import re

from ...base import StrSplitSolution, answer


def run(registers: tuple[int, ...], program: tuple[int, ...]) -> Iterator[int]:
    a, b, c = registers

    pointer = 0
    while pointer < len(program):
        opcode, operand = program[pointer : pointer + 2]
        combo = [0, 1, 2, 3, a, b, c][operand]

        match opcode:
            case 0:  # adv (A DiVide)
                a >>= combo
            case 1:  # bxl (B Xor Literal)
                b ^= operand
            case 2:  # bst (B STore)
                b = combo & 0b111
            case 3:  # jnz (Jump if Not Zero)
                if a:
                    pointer = operand
                    continue
            case 4:  # bxc (B Xor C)
                b ^= c
            case 5:  # out (OUTput)
                yield combo & 0b111
            case 6:  # bdv (B DiVide)
                b = a >> combo
            case 7:  # cdv (C DiVide)
                c = a >> combo
            case _:
                assert False, f"unexpected opcode {opcode}"

        pointer += 2


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 17.
    """
    _year = 2024
    _day = 17

    separator = "\n\n"

    @answer(("7,3,1,3,6,3,6,0,2", 105843716614554))
    def solve(self) -> tuple[str, int]:
        registers, program = (
            tuple(map(int, re.findall(r"\d+", block)))
            for block in self.input
        )
        program_output = ",".join(map(str, run(registers, program)))

        # HACK To make the problem tractable, we must make several
        # assumptions about the structure of the program: it is a loop
        # that, on each pass until A is 0, consumes 3 bits of A and
        # outputs one number. This allows us to build an A value 3 bits
        # at a time until the output matches the program.
        ADV_OPERAND = 3  # Our program will include an "adv 3"
        _, b, c = registers

        def quine_inputs(
                a_input: int = 0,
                num_digits: int = 0,
        ) -> Iterator[int]:
            output = tuple(run((a_input, b, c), program))
            # If the output matches the program, this A is a quine input
            if output == program:
                yield a_input
                return
            # If the output matches the program's last few digits, try
            # assigning the next bits of A
            if num_digits == 0 or output == program[-num_digits:]:
                for next_a_bits in range(1 << ADV_OPERAND):
                    yield from quine_inputs(
                        (a_input << ADV_OPERAND) | next_a_bits,
                        num_digits + 1,
                    )

        min_quine_input = min(quine_inputs())
        return program_output, min_quine_input
