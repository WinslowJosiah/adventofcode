from collections.abc import Iterable


def aoc2023_day03_part1(lines: Iterable[str]) -> int:
    schematic = list(lines)

    def verify_part_number(
            row: int,
            col_start: int,
            col_end: int,
            matrix: list[str],
    ) -> bool:
        """
        Verify whether the number found at row `row` and columns
        `col_start` to `col_end` is a part number.
        """
        height, width = len(matrix), len(matrix[0])

        for r in range(row - 1, row + 2):
            # Skip row if out of bounds
            if r < 0 or r >= width:
                continue
            for c in range(col_start - 1, col_end + 2):
                # Skip column if out of bounds
                if c < 0 or c >= height:
                    continue
                # Skip character if it's part of the number itself
                if r == row and col_start <= c <= col_end:
                    continue
                # If this character isn't a dot, this is a part number
                if matrix[r][c] != ".":
                    return True

        return False

    part_sum = 0
    # Iterate through rows and columns, and their indices
    for row, line in enumerate(schematic):
        # HACK: I would just loop through the iterator like normal, but
        # I need to skip multiple columns sometimes. If I give a name to
        # the iterator, I can call next() on it repeatedly to do this.
        col_iter = enumerate(line)
        for col, char in col_iter:
            # Skip non-digits
            if not char.isdigit():
                continue

            # This is the start of a number string
            num_start = col
            # Search for the end of the number string
            num_end = col
            while num_end < len(line) - 1 and line[num_end + 1].isdigit():
                num_end += 1
            # Collect the number string
            num_str = line[num_start:num_end + 1]
            # Add the number if it's a valid part number
            if verify_part_number(row, num_start, num_end, schematic):
                part_sum += int(num_str)

            # Skip columns until the end of the number is skipped
            for _ in range(num_end - col):
                next(col_iter)

    return part_sum


def aoc2023_day03_part2(lines: Iterable[str]) -> int:
    from math import prod

    schematic = list(lines)

    def gear_ratio(row: int, col: int, matrix: list[str]) -> int:
        """
        Calculate the gear ratio of the `*` character at row `row` and
        column `col` in `matrix`.
        """
        height, width = len(matrix), len(matrix[0])

        numbers: list[int] = []
        for r in range(row - 1, row + 2):
            # Skip row if out of bounds
            if r < 0 or r >= width:
                continue

            line = matrix[r]
            # HACK: I need to skip some columns again, so I'm using
            # another iterator.
            c_iter = iter(range(col - 1, col + 2))
            for c in c_iter:
                # Skip column if out of bounds
                if c < 0 or c >= height:
                    continue

                # Skip non-digits
                if not matrix[r][c].isdigit():
                    continue
                # We'll gather the number string containing this digit

                # Search for the start of the number string
                num_start = c
                while num_start > 0 and line[num_start - 1].isdigit():
                    num_start -= 1
                # Search for the end of the number string
                num_end = c
                while num_end < len(line) - 1 and line[num_end + 1].isdigit():
                    num_end += 1

                # Collect the number string
                num_str = line[num_start:num_end + 1]
                # Add the number to our list of numbers
                numbers.append(int(num_str))

                # Skip columns until the end of the number is skipped
                for _ in range(num_end - c):
                    try:
                        next(c_iter)
                    # This time, we have to worry about this exception
                    # that occurs if we go past the end of our range
                    # (but we can safely ignore it)
                    except StopIteration:
                        break

        # If there aren't exactly two numbers
        if len(numbers) != 2:
            # This isn't a gear; its gear ratio is 0
            return 0

        return prod(numbers)

    gear_sum = 0
    # Iterate through rows and columns, and their indices
    for row, line in enumerate(schematic):
        for col, char in enumerate(line):
            # Skip non-stars
            if char != "*":
                continue
            # Add gear ratio to total
            gear_sum += gear_ratio(row, col, schematic)

    return gear_sum


parts = (aoc2023_day03_part1, aoc2023_day03_part2)
