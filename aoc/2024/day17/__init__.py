from collections.abc import Iterable, Iterator
from typing import TypeAlias


Registers: TypeAlias = dict[str, int]
Program: TypeAlias = list[int]


def parse_program(lines: Iterable[str]) -> tuple[Program, Registers]:
    """
    Parse a series of input lines, and return a program and the initial
    register values.
    """
    line_iter = iter(lines)
    # Get register values until first blank line
    registers: Registers = {}
    for line in line_iter:
        if not line:
            break
        register, value = line.removeprefix("Register ").split(": ")
        registers[register] = int(value)

    # The program is a list of comma-separated numbers on the next line
    program: Program = list(map(int,
        next(line_iter).removeprefix("Program: ").split(",")
    ))
    # Instructions are between 0 and 7
    assert all(0 <= v <= 7 for v in program), \
        "Program contains invalid instructions!"

    return program, registers


def run_program(program: Program, registers: Registers) -> Iterator[int]:
    """
    Run a program on The Historians' computer, and yield its outputs.
    """
    def combo_operand(value: int) -> int:
        match value:
            case value if 0 <= value <= 3:
                return value
            case 4:
                return registers["A"]
            case 5:
                return registers["B"]
            case 6:
                return registers["C"]
            case _:
                raise RuntimeError("Combo operand is reserved")

    pointer = 0
    while pointer < len(program):
        match program[pointer:pointer + 2]:
            case 0, operand:  # adv (A DiVide)
                registers["A"] >>= combo_operand(operand)
            case 1, operand:  # bxl (B Xor Literal)
                registers["B"] ^= operand
            case 2, operand:  # bst (B STore)
                registers["B"] = combo_operand(operand) & 0b111
            case 3, operand:  # jnz (Jump if Not Zero)
                if registers["A"]:
                    # NOTE I subtract 2 so that moving to the next
                    # instruction will set the pointer to the operand.
                    pointer = operand - 2
            case 4, _:  # bxc (B Xor C)
                registers["B"] ^= registers["C"]
            case 5, operand:  # out (OUTput)
                yield combo_operand(operand) & 0b111
            case 6, operand:  # bdv (B DiVide)
                registers["B"] = registers["A"] >> combo_operand(operand)
            case 7, operand:  # cdv (C DiVide)
                registers["C"] = registers["A"] >> combo_operand(operand)
            case _:  # Default case
                # This shouldn't happen
                assert False

        pointer += 2


def aoc2024_day17_part1(lines: Iterable[str]) -> str:
    program, registers = parse_program(lines)
    # NOTE The output is in the form of a string, unlike the other
    # Advent of Code challenges this year.
    return ",".join(map(str, run_program(program, registers)))


def aoc2024_day17_part2(lines: Iterable[str]) -> int:
    import itertools as it

    program, registers = parse_program(lines)
    # NOTE This solution is based on the assumption that the program is
    # a giant loop that outputs one number and shifts register A by a
    # constant amount each time until register A is 0.

    # Find the adv opcode (which shifts A to the right), and get the
    # amount it shifts by
    SHIFT = next((
        operand
        for opcode, operand in it.batched(program, 2)
        # NOTE The operand is a combo operand, so the shift amount isn't
        # guaranteed to be constant unless it's between 0 and 3.
        if opcode == 0 and 0 <= operand <= 3
    ), 0)
    assert SHIFT > 0, "expected register A to be shifted"
    # The calculations will depend on the shifted-in bits of A, and up
    # to 7 other bits
    # NOTE This is because there is a cdv instruction where, at that
    # point in the program, the maximum shift amount would be 7.
    INPUT_BITS = 7 + SHIFT

    # Cache the first output for every considered value of A
    output_cache = {
        a: next(run_program(program, registers | {"A": a}))
        for a in range(1 << INPUT_BITS)
    }

    # Recursively find every input that outputs the program
    def find_quine_inputs() -> Iterator[int]:
        if not program:
            return

        def helper(a: int, pointer: int = 0) -> Iterator[int]:
            # Yield if every number of the program was outputted
            if pointer >= len(program):
                yield a
                return

            # For each possible set of shifted-in bits
            for next_bits in range(1 << SHIFT):
                # Calculate what A would be with these bits in front
                next_bits_shift = INPUT_BITS + (pointer - 1) * SHIFT
                next_a = a | (next_bits << next_bits_shift)

                inp = next_a >> (pointer * SHIFT)
                # If the correct value would be outputted at this point
                # with these bits
                if output_cache[inp] == program[pointer]:
                    # Check the next number in the program
                    yield from helper(next_a, pointer + 1)

        # Start with each input that outputs the first number of the
        # program
        for inp, out in output_cache.items():
            if out == program[0]:
                yield from helper(inp, 1)

    # Find the minimum input that outputs the program
    answer = min(find_quine_inputs(), default=None)
    assert answer is not None, "no quine input found"
    return answer


parts = (aoc2024_day17_part1, aoc2024_day17_part2)
