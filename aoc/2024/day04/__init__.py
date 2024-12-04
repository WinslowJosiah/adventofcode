from collections.abc import Iterable


def aoc2024_day04_part1(lines: Iterable[str]) -> int:
    # Input is a list of rows
    rows = list(lines)
    height, width = len(rows), len(rows[0])

    # Construct columns
    columns = ["".join(column) for column in zip(*rows)]

    # Construct main/anti diagonals
    main_diagonals = ["" for _ in range(width + height - 1)]
    anti_diagonals = ["" for _ in range(width + height - 1)]
    for r in range(height):
        for c in range(width):
            anti_diagonals[c + r] += rows[r][c]
            main_diagonals[c - r + height - 1] += rows[r][c]

    word_lines = rows + columns + main_diagonals + anti_diagonals
    # Count word (and its reverse) across all possible word lines
    return sum(
        word_line.count(word)
        for word_line in word_lines
        for word in ("XMAS", "SAMX")
    )


def aoc2024_day04_part2(lines: Iterable[str]) -> int:
    # Input is a list of rows
    rows = list(lines)
    height, width = len(rows), len(rows[0])

    total = 0
    # For every potential middle A spot in the grid
    # NOTE The X-shape will extend one letter outwards in all 4 diagonal
    # directions, so we skip a 1 tile thick border of letters.
    for r in range(1, height - 1):
        for c in range(1, width - 1):
            # This letter should be an A
            if rows[r][c] != "A":
                continue
            # The letters on the main diagonal should be MS or SM
            main_diagonal = rows[r - 1][c - 1] + rows[r + 1][c + 1]
            if main_diagonal not in ("MS", "SM"):
                continue
            # The letters on the anti diagonal should be MS or SM
            anti_diagonal = rows[r + 1][c - 1] + rows[r - 1][c + 1]
            if anti_diagonal not in ("MS", "SM"):
                continue

            # If we're here, this is a valid X-MAS
            total += 1

    return total


parts = (aoc2024_day04_part1, aoc2024_day04_part2)
