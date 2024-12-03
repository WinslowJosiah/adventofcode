from collections import defaultdict, deque
from collections.abc import Iterable
from enum import Enum


class Direction(Enum):
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    WEST = (0, -1)
    EAST = (0, 1)


class Beam:
    def __init__(
            self,
            row: int,
            col: int,
            dir: Direction | tuple[int, int],
    ):
        self.row = row
        self.col = col
        if isinstance(dir, Direction):
            dir = dir.value
        self.delta_row, self.delta_col = dir

    def __str__(self):
        return (
            f"({self.row}, {self.col}, "
            f"{str(Direction((self.delta_row, self.delta_col)))})"
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.row}, {self.col}, "
            f"{repr(Direction((self.delta_row, self.delta_col)))})"
        )

    def copy(self):
        return self.__class__(
            self.row, self.col, (self.delta_row, self.delta_col),
        )

    def move_forward(self):
        self.row += self.delta_row
        self.col += self.delta_col
        return self

    def in_bounds(self, height: int, width: int):
        return 0 <= self.row < height and 0 <= self.col < width

    def turn_left(self):
        self.delta_row, self.delta_col = -self.delta_col, self.delta_row
        return self

    def turn_right(self):
        self.delta_row, self.delta_col = self.delta_col, -self.delta_row
        return self

    def reflect_main_diagonal(self):
        self.delta_row, self.delta_col = self.delta_col, self.delta_row
        return self

    def reflect_anti_diagonal(self):
        self.delta_row, self.delta_col = -self.delta_col, -self.delta_row
        return self


def propagate_beam(beam: Beam, grid: list[str]) -> int:
    """
    Propagate `beam` through a grid of tiles from the beam's starting
    position, until there are no active beams. Returns the number of
    tiles that were "energized" by being visited by a beam.
    """
    height = len(grid)
    width = len(grid[0])

    # This set stores the positions of every tile that is energized, and
    # the directions from which they've been visited
    energized: defaultdict[tuple[int, int], set[tuple[int, int]]] = \
        defaultdict(set)

    # NOTE: We store all of the active beams in a deque, and process
    # each of them from front to back. This makes it extremely efficient
    # to remove and split beams, as compared to (say) a list of beams.
    beams = deque([beam])
    # While there are beams left to propagate
    while beams:
        beam = beams.popleft()
        # If beam is out of bounds, don't propagate any further
        if not beam.in_bounds(height, width):
            continue

        beam_pos = (beam.row, beam.col)
        beam_dir = (beam.delta_row, beam.delta_col)
        # If tile was visited from this direction before, don't
        # propagate any further
        if beam_dir in energized.get(beam_pos, set()):
            continue

        tile_was_energized = beam_pos in energized
        # This tile is now energized
        energized[beam_pos].add(beam_dir)

        tile = grid[beam.row][beam.col]
        # If tile is / mirror
        if tile == "/":
            # Reflect along it
            beam.reflect_anti_diagonal()
        # If tile is \ mirror
        elif tile == "\\":
            # Reflect along it
            beam.reflect_main_diagonal()
        # If tile is splitter, and beam is moving perpendicular to it
        elif (
            (tile == "-" and beam.delta_row)
            or (tile == "|" and beam.delta_col)
        ):
            # If tile was already energized (and beam was already split
            # here), don't propagate any further
            if tile_was_energized:
                continue

            # The beam splits into two beams, one of which turns left,
            # and one of which turns right
            beams.append(beam.copy().turn_left().move_forward())
            beam.turn_right()
        # NOTE: If none of the previous conditions were met, the tile is
        # either empty space, or being treated like empty space.

        # Move the beam forward
        beams.append(beam.move_forward())

    # Count the number of energized tiles
    return len(energized)


def aoc2023_day16_part1(lines: Iterable[str]) -> int:
    grid = list(lines)
    # Beam starts at top-left corner going east
    return propagate_beam(Beam(0, 0, Direction.EAST), grid)


def aoc2023_day16_part2(lines: Iterable[str]) -> int:
    from itertools import chain

    grid = list(lines)
    height = len(grid)
    width = len(grid[0])

    # Result is maximum for all beams starting on the edge going inwards
    return max(chain(
        (
            propagate_beam(Beam(0, j, Direction.SOUTH), grid)
            for j in range(width)
        ),
        (
            propagate_beam(Beam(height - 1, j, Direction.NORTH), grid)
            for j in range(width)
        ),
        (
            propagate_beam(Beam(i, 0, Direction.EAST), grid)
            for i in range(height)
        ),
        (
            propagate_beam(Beam(i, width - 1, Direction.WEST), grid)
            for i in range(height)
        ),
    ))


parts = (aoc2023_day16_part1, aoc2023_day16_part2)
