from collections import deque
from collections.abc import Iterable
from itertools import starmap
from operator import add


type Vector = tuple[int, ...]


def count_paths(
        src_node: Vector,
        path_length: int,
        grid: list[str],
) -> int:
    """
    Count the number of paths with a length of `path_length` from
    `src_node` in a grid of tiles. The paths are allowed to double back
    on themselves.
    """
    result = 0

    height = len(grid)
    width = len(grid[0])

    visited: set[Vector] = set()
    # This is basically a standard breadth-first search
    queue: deque[tuple[int, Vector]] = deque([(0, src_node)])
    while queue:
        cost, node = queue.popleft()

        # If node has been visited before
        if node in visited:
            # Don't explore this path any further
            continue
        visited.add(node)

        # If the current path's parity is the same as the parity of the
        # specified path length
        if cost % 2 == path_length % 2:
            # This path can be reached in the specified number of steps
            result += 1
            # NOTE: We can do this because all paths between any two
            # tiles will have the same parity.
        # If path becomes longer than specified path length
        if cost >= path_length:
            # Don't explore this path any further
            continue

        for offset in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            # Get coordinates at offset
            next_row, next_col = starmap(add, zip(node, offset))
            # If this plot of land is not empty
            if grid[next_row % height][next_col % width] == "#":
                # This neighbor is not valid
                continue
            # Append this neighbor to the queue
            queue.append((cost + 1, (next_row, next_col)))

    return result


def aoc2023_day21_part1(lines: Iterable[str]) -> int:
    grid = list(lines)
    height = len(grid)
    width = len(grid[0])
    # The elf starts in the center of the grid
    return count_paths((height // 2, width // 2), 64, grid)


def aoc2023_day21_part2(lines: Iterable[str]) -> int:
    steps_to_take = 26501365

    grid = list(lines)
    height = len(grid)
    width = len(grid[0])
    # XXX: I hate how simple this looks. I hate how complicated the
    # problem was. I hate how many assumptions I needed to make about
    # the input data to even start arriving at a formula for the answer.
    # I hate how these assumptions were not a part of the specifications
    # or the example data. I hate how the formula I arrived at didn't
    # work. I hate how even other people's formulas didn't work for my
    # input. I hate how I know after all of this that the answer is the
    # result of some quadratic equation that I couldn't derive myself
    # and that I don't even know the coefficients of. I hate, hate,
    # hate, hate, hate, hate, hate this problem. Get it out of my sight.

    n = steps_to_take // width
    # The elf starts in the center of the grid
    a, b, c = (
        count_paths((height // 2, width // 2), s * width + (width // 2), grid)
        for s in range(3)
    )
    # NOTE: This part of my solution comes verbatim from someone else.
    # (No, I won't explain it. No, I'm not sorry.)
    return a + n * (b - a + (n - 1) * (c - b - b + a) // 2)


parts = (aoc2023_day21_part1, aoc2023_day21_part2)
