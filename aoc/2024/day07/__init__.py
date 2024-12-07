from collections.abc import Iterable
import itertools as it


def aoc2024_day07_part1(lines: Iterable[str]) -> int:
    total = 0
    for line in lines:
        value, operands = line.split(": ")
        value = int(value)
        operands = [int(n) for n in operands.split()]

        # For every way to fill in the operators
        for operators in it.product("*+", repeat=len(operands) - 1):
            result = operands[0]
            # Apply the operators from left to right
            for operator, operand in zip(operators, operands[1:]):
                if operator == "+":
                    result += operand
                elif operator == "*":
                    result *= operand

                # Quit early if the result is too big
                # NOTE We can do this because the operations will only
                # ever increase the result.
                if result > value:
                    break
            # If we did not quit early
            else:
                # If our result matches the value, add it to the total
                if result == value:
                    total += value
                    break

    return total


def aoc2024_day07_part2(lines: Iterable[str]) -> int:
    total = 0
    for line in lines:
        value, operands = line.split(": ")
        value = int(value)
        operands = [int(n) for n in operands.split()]

        # For every way to fill in the operators
        for operators in it.product("*+|", repeat=len(operands) - 1):
            result = operands[0]
            # Apply the operators from left to right
            for operator, operand in zip(operators, operands[1:]):
                if operator == "+":
                    result += operand
                elif operator == "*":
                    result *= operand
                elif operator == "|":
                    result = int(str(result) + str(operand))

                # Quit early if the result is too big
                # NOTE We can do this because the operations will only
                # ever increase the result.
                if result > value:
                    break
            # If we did not quit early
            else:
                # If our result matches the value, add it to the total
                if result == value:
                    total += value
                    break

    return total


parts = (aoc2024_day07_part1, aoc2024_day07_part2)
