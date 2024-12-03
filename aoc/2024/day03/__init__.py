from collections.abc import Iterable
import re


def aoc2024_day03_part1(lines: Iterable[str]) -> int:
    # This regex matches a mul() instruction, and groups its arguments
    mul_regex = re.compile(r"mul\((\d+),(\d+)\)")

    total = 0
    for line in lines:
        for match in mul_regex.finditer(line):
            total += int(match[1]) * int(match[2])
    return total


def aoc2024_day03_part2(lines: Iterable[str]) -> int:
    # This regex matches any of the three kinds of instructions
    instruction_regex = re.compile(
        # mul(arg1,arg2)
        r"(?P<mul>mul)\((?P<mul_arg1>\d+),(?P<mul_arg2>\d+)\)"
        # do()
        r"|(?P<do>do)\(\)"
        # don't()
        r"|(?P<dont>don't)\(\)"
    )

    total = 0
    do = True  # We start off able to multiply
    for line in lines:
        for match in instruction_regex.finditer(line):
            if match["do"]:
                do = True
            elif match["dont"]:
                do = False
            # NOTE We only multiply if the most recent do/don't command
            # was do().
            elif match["mul"] and do:
                total += int(match["mul_arg1"]) * int(match["mul_arg2"])

    return total


parts = (aoc2024_day03_part1, aoc2024_day03_part2)
