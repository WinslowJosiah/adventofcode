# https://adventofcode.com/2025/day/10

from itertools import combinations, product

from ...base import StrSplitSolution, answer


type Wiring = set[int]
type Matrix = list[list[int]]


def parse_machine(line: str) -> tuple[Wiring, list[Wiring], list[int]]:
    raw_indicators, *raw_buttons, raw_joltages = (
        part[1:-1] for part in line.split()
    )
    indicators = {i for i, ch in enumerate(raw_indicators) if ch == "#"}
    buttons = [
        set(map(int, raw_button.split(",")))
        for raw_button in raw_buttons
    ]
    joltages = list(map(int, raw_joltages.split(",")))
    return indicators, buttons, joltages


def configure_indicators(buttons: list[Wiring], indicators: Wiring) -> int:
    for num_presses in range(1, len(buttons) + 1):
        # NOTE Pressing a button twice does nothing, so we never need to
        # press a button more than once.
        for button_combo in combinations(buttons, num_presses):
            lights: Wiring = set()
            for button in button_combo:
                lights ^= button
            if lights == indicators:
                return num_presses
    assert False, "solution not found"


def configure_joltages(buttons: list[Wiring], joltages: list[int]) -> int:
    matrix = [[0] * (len(buttons) + 1) for _ in range(len(joltages))]
    # Left columns have button wirings
    for i, button in enumerate(buttons):
        for j in button:
            matrix[j][i] = 1
    # Rightmost column has target joltages
    for i, joltage in enumerate(joltages):
        matrix[i][-1] = joltage
    # Solve for number of button presses for each button
    matrix, free_vars = integer_gaussian_elimination(matrix)

    min_presses = None
    # Try all possible assignments to free variables
    assignment_ranges = [range(max(joltages) + 1) for _ in free_vars]
    for assignment in product(*assignment_ranges):
        num_presses = sum(assignment)
        # Skip if already worse than the best found
        if min_presses is not None and num_presses >= min_presses:
            continue

        # Check that all determined variables are valid
        for row in matrix:
            pivot = next((val for val in row if val), 0)
            # Skip this row if it has no determined variable
            if not pivot:
                continue
            # Compute value of determined variable
            row_presses = row[-1]
            for index, value in zip(free_vars, assignment):
                row_presses -= row[index] * value
            # Determined variable must be a non-negative integer
            row_presses, remainder = divmod(row_presses, pivot)
            if remainder or row_presses < 0:
                break

            num_presses += row_presses
            # Stop early if already worse than the best found
            if min_presses is not None and num_presses >= min_presses:
                break
        else:
            # A more minimal solution was found
            min_presses = num_presses

    assert min_presses is not None
    return min_presses


def integer_gaussian_elimination(matrix: Matrix) -> tuple[Matrix, list[int]]:
    num_cols = len(matrix[0])

    current_row = 0
    free_vars: list[int] = []
    # Elimination step
    for current_col in range(num_cols - 1):
        # Find a row with a pivot in this column and swap
        for pivot_row, row in enumerate(matrix[current_row:], current_row):
            if row[current_col]:
                break
        else:
            # No pivot found; this column is a free variable
            free_vars.append(current_col)
            continue
        matrix[current_row], matrix[pivot_row] = (
            matrix[pivot_row], matrix[current_row]
        )

        # Zero out other entries in this column using row operations
        for r, row in enumerate(matrix):
            # Don't zero out this row
            if r == current_row:
                continue
            coeff = row[current_col]
            for c, val in enumerate(row):
                # NOTE This is a different formula from usual, which
                # avoids using floats or fractions.
                row[c] = (
                    val * matrix[current_row][current_col]
                    - matrix[current_row][c] * coeff
                )

        # Move on to next row
        current_row += 1

    # Check for inconsistency (i.e. no solutions)
    for r in range(len(matrix)):
        if not any(matrix[r][:-1]) and matrix[r][-1]:
            raise ValueError("inconsistent system")

    return matrix, free_vars


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 10.
    """
    _year = 2025
    _day = 10

    @answer((542, 20871))
    def solve(self) -> tuple[int, int]:
        num_indicator_presses, num_joltage_presses = 0, 0
        for line in self.input:
            indicators, buttons, joltages = parse_machine(line)
            num_indicator_presses += configure_indicators(buttons, indicators)
            num_joltage_presses += configure_joltages(buttons, joltages)
        return num_indicator_presses, num_joltage_presses
