from collections.abc import Iterable


def aoc2023_day14_part1(lines: Iterable[str]) -> int:
    def sum_of_range(start: int, stop: int) -> int:
        """
        Calculate the sum of the range of numbers from `start`
        (inclusive) to `stop` (inclusive).
        """
        if start > stop:
            return 0
        return (start + stop) * (stop - start + 1) // 2

    # Gather the grid from the input
    grid = list(lines)
    height = len(grid)
    width = len(grid[0])

    load_sum = 0
    # For each column in the grid
    for col in range(width):
        col_str = "".join(grid[r][col] for r in range(height))

        # The highest load for a rock in this section
        load = height
        # For each section stopped by a cube-shaped rock
        for section in col_str.split("#"):
            # Count the number of rounded rocks
            rock_count = section.count("O")
            # NOTE: If all the rounded rocks were rolled to the north,
            # the load for each of them is a range of numbers ending at
            # the highest load number, with however many numbers as
            # there are rocks.
            load_sum += sum_of_range(load - rock_count + 1, load)
            # Calculate the highest load for a rock in the next section
            load -= len(section) + 1

    return load_sum


def aoc2023_day14_part2(lines: Iterable[str]) -> int:
    from collections.abc import Sequence
    from itertools import islice

    cycle_count = 1_000_000_000

    def tilt_west(grid: Sequence[Sequence[str]]) -> list[str]:
        """
        Return the result of taking a grid of characters, and moving all
        `O` characters to the west until they hit a `#` character or the
        edge of the grid.
        """
        return [
            # Join together, with a "#"...
            "#".join(
                # ...every rounded rock in this section, rolled all the
                # way to the west...
                ("O" * section.count("O")).ljust(len(section), ".")
                # ...for every "#"-delimited section in this row...
                for section in "".join(row).split("#")
            )
            # ...for every row in the grid
            for row in grid
        ]

    def tilt_east(grid: Sequence[Sequence[str]]) -> list[str]:
        """
        Return the result of taking a grid of characters, and moving all
        `O` characters to the east until they hit a `#` character or the
        edge of the grid.
        """
        return [
            # Join together, with a "#"...
            "#".join(
                # ...every rounded rock in this section, rolled all the
                # way to the east...
                ("O" * section.count("O")).rjust(len(section), ".")
                # ...for every "#"-delimited section in this row...
                for section in "".join(row).split("#")
            )
            # ...for every row in the grid
            for row in grid
        ]

    # NOTE: I have only defined functions for tilting the grid to the
    # west and the east. Because of how I represent the grid as a
    # sequence of rows, it's more convenient to operate on each row than
    # to operate on each column. Therefore, to tilt north/south, I
    # transpose the grid, tilt west/east, and transpose the grid again.
    def transpose(grid: Sequence[Sequence[str]]) -> list[tuple[str, ...]]:
        """
        Transpose a grid represented as a list of strings; this will
        turn the rows into columns, and the columns into rows.
        """
        return list(zip(*grid))

    def cycle(grid: Sequence[Sequence[str]]) -> list[str]:
        """
        Perform a "spin-cycle" on a grid of characters.

        The "spin-cycle" consists of tilting the grid to the north, then
        tilting the grid to the west, then tilting the grid to the
        south, then tilting the grid to the east.
        """
        # Tilt north (transpose, tilt west, and un-transpose), then west
        grid = tilt_west(transpose(tilt_west(transpose(grid))))
        # Tilt south (transpose, tilt east, and un-transpose), then east
        grid = tilt_east(transpose(tilt_east(transpose(grid))))

        return grid

    # Gather the grid from the input
    grid = list(lines)
    # We will cache each grid found so far, along with the cycle index
    # at which each grid was first reached
    # NOTE: We are using a dict as our cache. To check whether a grid
    # has been found before in constant time, we store the grids as keys
    # and the indices as values. Also, because dict keys must be
    # hashable, the grids are not stored as lists, but tuples.
    grids: dict[tuple[str, ...], int] = {}

    # For each spin-cycle we need to perform
    for i in range(cycle_count):
        grid_tuple = tuple(grid)
        # If this grid state has been reached before
        if grid_tuple in grids:
            # We are in some constant-length loop
            # Get the index that is looped back to
            prev_i = grids[grid_tuple]
            # Calculate the length of the loop
            loop_length = i - prev_i
            # Calculate the index looped back to after the necessary
            # amount of spin-cycles have been performed
            target_i = prev_i + ((cycle_count - prev_i) % loop_length)

            # NOTE: Since Python 3.7, dicts are guaranteed to have their
            # keys stored in the same order that they were inserted in.
            # So because we inserted the grids as keys in order anyway
            # (and we used the 0-based index as their values), we just
            # need to get the nth key of the dict in order.
            grid = next(islice(grids.keys(), target_i, target_i + 1))

            # We have the final grid; we can stop spin-cycling
            break

        # Store this grid state with its index
        grids[grid_tuple] = i
        # Perform one spin-cycle
        grid = cycle(grid)

    # The total load for this grid is the sum...
    return sum(
        # ...of the loads of all rounded rocks in the row...
        row_load * row.count("O")
        # ...for every row in the grid
        for row_load, row in zip(range(len(grid), 0, -1), grid)
    )


parts = (aoc2023_day14_part1, aoc2023_day14_part2)
