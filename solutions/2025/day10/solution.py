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
    # NOTE Each machine's buttons/joltages can be modeled as a system of
    # equations, which itself can be modeled as an "augmented matrix".
    # Putting this matrix in "row echelon form" helps us find solutions;
    # we want to find a nonnegative integer solution with a minimal sum
    # (i.e. the minimum number of button presses).
    matrix = build_augmented_matrix(buttons, joltages)
    free_vars = integer_row_echelon_inplace(matrix)

    min_presses = None
    # We may have some "free variables" upon which the other variables
    # depend; try all assignments of values to those free variables
    # NOTE We only try values up to the highest target joltage, as more
    # button presses than that would increase the joltage too much.
    assignment_ranges = [range(max(joltages) + 1) for _ in free_vars]
    for free_var_values in product(*assignment_ranges):
        num_presses = sum(free_var_values)
        # Skip if already worse than the best found
        if min_presses is not None and num_presses >= min_presses:
            continue

        # Check that all determined variables (in columns without
        # pivots) are valid
        for row in matrix:
            # Find the pivot value (first nonzero entry)
            pivot = next((val for val in row[:-1] if val), None)
            if pivot is None:
                continue
            # Use back-substitution to compute determined variable
            # NOTE This is possible because the only nonzero values in
            # the row are the pivot, the free variables, and the RHS.
            row_presses = row[-1]
            for index, value in zip(free_vars, free_var_values):
                row_presses -= row[index] * value
            row_presses, remainder = divmod(row_presses, pivot)
            # Determined variable must be a non-negative integer
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


def build_augmented_matrix(
        buttons: list[Wiring],
        joltages: list[int],
) -> Matrix:
    """
    Build augmented matrix where columns represent button wirings, and
    rows represent joltage level results.
    """
    matrix = [[0] * (len(buttons) + 1) for _ in range(len(joltages))]
    # Each button column shows which joltage levels it affects
    for button_index, button in enumerate(buttons):
        for joltage_index in button:
            matrix[joltage_index][button_index] = 1
    # Rightmost column is the target joltages
    for joltage_index, joltage in enumerate(joltages):
        matrix[joltage_index][-1] = joltage
    return matrix


def integer_row_echelon_inplace(matrix: Matrix) -> list[int]:
    """
    Put matrix in row echelon form.

    The matrix is modified in-place. The column indices of any free
    variables (columns without pivots) are returned. The resulting
    matrix will have the following properties:

    - All rows whose only entries are zero are at the bottom.
    - The pivot (leftmost nonzero entry) of every non-zero row is to the
    right of the pivot of the row above.
    - Each column with a pivot has zeros in all of its other entries.

    This is similar to reduced row echelon form, except the requirement
    of all pivots being 1 is relaxed. 

    Parameters
    ----------
    matrix : list of list of int
        Matrix to put in row echelon form. This is modified in-place.

    Returns
    -------
    list of int
        Column indices of free variables.
    """
    num_cols = len(matrix[0])

    current_row = 0
    free_vars: list[int] = []
    # Elimination step
    for current_col in range(num_cols - 1):
        # Find a row with a pivot in this column and swap
        for pivot_row_index, row in enumerate(
            matrix[current_row:],
            start=current_row,
        ):
            if row[current_col]:
                break
        else:
            # No pivot found; this column is a free variable
            free_vars.append(current_col)
            continue
        matrix[current_row], matrix[pivot_row_index] = (
            matrix[pivot_row_index], matrix[current_row]
        )
        pivot_row = matrix[current_row]
        pivot = pivot_row[current_col]

        # Zero out other entries in this column using row operations
        for r, row in enumerate(matrix):
            # Don't zero out this row
            if r == current_row:
                continue
            coeff = row[current_col]
            for c, val in enumerate(row):
                # NOTE Instead of standard elimination, we use a variant
                # which preserves integer values and avoids division.
                # Standard: row[c] = row[c]
                #     - pivot_row[c] * row[current_col] / pivot
                #  Integer: row[c] = row[c] * pivot
                #     - pivot_row[c] * row[current_col]
                row[c] = val * pivot - pivot_row[c] * coeff

        # Move on to next row
        current_row += 1

    # Check for inconsistency (i.e. no solutions)
    for r in range(len(matrix)):
        if not any(matrix[r][:-1]) and matrix[r][-1]:
            raise ValueError("inconsistent system")

    return free_vars


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
