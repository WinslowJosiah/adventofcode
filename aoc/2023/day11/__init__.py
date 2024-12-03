from collections.abc import Iterable


def aoc2023_day11_part1(lines: Iterable[str]) -> int:
    from itertools import combinations

    expansion_offset = 1

    image = list(lines)

    # Precalculate empty columns
    empty_cols: set[int] = set()
    for col in range(len(image[0])):
        if all(image[row][col] == "." for row in range(len(image))):
            empty_cols.add(col)

    galaxies: list[tuple[int, int]] = []
    # NOTE: row_offset and col_offset are the offsets to add to the
    # galaxy positions, to account for the expanding space between them.
    row_offset = 0
    for row, line in enumerate(image):
        # If this line is empty
        if all(char == "." for char in line):
            # Space simply expands in it
            row_offset += expansion_offset
            continue

        col_offset = 0
        for col, char in enumerate(line):
            # If this column is empty
            if col in empty_cols:
                # Space simply expands in it
                col_offset += expansion_offset
                continue

            # If this row and column has a galaxy
            if char == "#":
                # Add it to the list of galaxies (taking into account
                # the expanding space)
                galaxies.append((row + row_offset, col + col_offset))

    distances_sum = 0
    # For each combination of 2 galaxies
    for galaxy1, galaxy2 in combinations(galaxies, r=2):
        row1, col1 = galaxy1
        row2, col2 = galaxy2
        # Add distance between galaxies
        distances_sum += abs(row1 - row2) + abs(col1 - col2)

    return distances_sum


def aoc2023_day11_part2(lines: Iterable[str]) -> int:
    from itertools import combinations

    # This is literally the only change!
    expansion_offset = 999999

    image = list(lines)

    empty_cols: set[int] = set()
    for col in range(len(image[0])):
        if all(image[row][col] == "." for row in range(len(image))):
            empty_cols.add(col)

    galaxies: list[tuple[int, int]] = []
    row_offset = 0
    for row, line in enumerate(image):
        if all(char == "." for char in line):
            row_offset += expansion_offset
            continue

        col_offset = 0
        for col, char in enumerate(line):
            if col in empty_cols:
                col_offset += expansion_offset
                continue

            if char == "#":
                galaxies.append((row + row_offset, col + col_offset))

    distances_sum = 0
    for galaxy1, galaxy2 in combinations(galaxies, r=2):
        row1, col1 = galaxy1
        row2, col2 = galaxy2
        distances_sum += abs(row1 - row2) + abs(col1 - col2)

    return distances_sum


parts = (aoc2023_day11_part1, aoc2023_day11_part2)
