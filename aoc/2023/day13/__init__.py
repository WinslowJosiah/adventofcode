from collections.abc import Iterable


def aoc2023_day13_part1(lines: Iterable[str]) -> int:
    from itertools import pairwise

    def find_row_symmetry_line(grid: list[str]) -> int | None:
        """
        Find the index before the line of symmetry in a grid of
        characters. Only the horizontal lines of symmetry are checked.
        """
        # For each pair of adjacent rows
        for i, (row1, row2) in enumerate(pairwise(grid)):
            # Skip if the rows aren't equal
            if row1 != row2:
                continue
            # If the rows are equal, the line between them is a possible
            # line of symmetry

            # Check each pair of symmetric rows along this line
            for before_i, after_i in zip(
                range(i - 1, -1, -1),
                range(i + 2, len(grid)),
            ):
                # If the rows do not match
                if grid[before_i] != grid[after_i]:
                    # This is not a valid line of symmetry
                    break
            # If every row matches
            else:
                # This is the line of symmetry
                return i
        # NOTE: If no line of symmetry is found, None is implicitly
        # returned.

    note_sum = 0
    line_iter = iter(lines)
    # Don't worry, this loop eventually ends!
    while True:
        # Collect grid of ash and rocks
        grid: list[str] = []
        for line in line_iter:
            # Each grid is separated by an empty line
            if not line:
                break
            grid.append(line)

        # If the current grid is empty, there was no grid to collect,
        # and we can end the loop
        if not grid:
            break

        # Try finding a line of symmetry along the rows
        symmetry_line = find_row_symmetry_line(grid)
        # If a line of symmetry was found
        if symmetry_line is not None:
            # We add 100 for each row above the line
            note_sum += 100 * (symmetry_line + 1)
            continue

        # Transpose the grid, so the rows become columns and vice versa
        grid = list(zip(*grid))

        # Try finding a line of symmetry along the columns
        symmetry_line = find_row_symmetry_line(grid)
        # If a line of symmetry was found
        if symmetry_line is not None:
            # We add 1 for each column before the line
            note_sum += symmetry_line + 1
            continue

    return note_sum


def aoc2023_day13_part2(lines: Iterable[str]) -> int:
    from itertools import pairwise

    def find_row_symmetry_line(
            grid: list[str],
            total_smudges: int = 1,
    ) -> int | None:
        """
        Find the index before the line of symmetry in a grid of
        characters. Only the horizontal lines of symmetry are checked.

        The lines that are found will have some amount of "smudges" on
        either side of them (1 by default), i.e. they would be perfect
        reflections if that many characters were changed on one side.
        """
        # For each pair of adjacent rows
        for i, (row1, row2) in enumerate(pairwise(grid)):
            # Skip if the rows aren't equal or "smudged"
            # NOTE: When summed together, boolean values are treated as
            # numbers. True is treated as 1, and False is treated as 0.
            smudges = sum(
                char1 != char2
                for char1, char2 in zip(row1, row2)
            )
            if smudges > total_smudges:
                continue
            # If the rows are close enough to being equal, the line
            # between them is a possible line of symmetry

            extra_smudges = 0
            # Check each pair of symmetric rows along this line
            for before_i, after_i in zip(
                range(i - 1, -1, -1),
                range(i + 2, len(grid)),
            ):
                # Count the extra smudges these rows would contain
                extra_smudges += sum(
                    char1 != char2
                    for char1, char2 in zip(grid[before_i], grid[after_i])
                )
                # If there are too many smudges
                if smudges + extra_smudges > total_smudges:
                    # This is not a valid line of symmetry
                    break
            # If every row matches
            else:
                # If there are exactly the correct amount of smudges
                if smudges + extra_smudges == total_smudges:
                    # This is the line of symmetry
                    return i
        # NOTE: If no line of symmetry is found, None is implicitly
        # returned.

    note_sum = 0
    line_iter = iter(lines)
    # Don't worry, this loop eventually ends!
    while True:
        # Collect grid of ash and rocks
        grid: list[str] = []
        for line in line_iter:
            # Each grid is separated by an empty line
            if not line:
                break
            grid.append(line)

        # If the current grid is empty, there was no grid to collect,
        # and we can end the loop
        if not grid:
            break

        # Try finding a line of symmetry along the rows
        symmetry_line = find_row_symmetry_line(grid)
        # If a line of symmetry was found
        if symmetry_line is not None:
            # We add 100 for each row above the line
            note_sum += 100 * (symmetry_line + 1)
            continue

        # Transpose the grid, so the rows become columns and vice versa
        grid = list(zip(*grid))

        # Try finding a line of symmetry along the columns
        symmetry_line = find_row_symmetry_line(grid)
        # If a line of symmetry was found
        if symmetry_line is not None:
            # We add 1 for each column before the line
            note_sum += symmetry_line + 1
            continue

    return note_sum


parts = (aoc2023_day13_part1, aoc2023_day13_part2)
