# https://adventofcode.com/2024/day/15

from collections.abc import Iterable

from ...base import StrSplitSolution, answer
from ...utils.grids import Direction, Grid, GridPoint, add_points, parse_grid


# Move characters + direction offset of this move
MOVE_OFFSETS = {
    ">": Direction.RIGHT.offset,
    "v": Direction.DOWN.offset,
    "<": Direction.LEFT.offset,
    "^": Direction.UP.offset,
}
# Box characters + offsets to the tiles of the box
BOX_OFFSETS: dict[str, list[GridPoint]] = {
    "O": [(0, 0)],
    "[": [(0, 0), Direction.RIGHT.offset],
    "]": [(0, 0), Direction.LEFT.offset],
}


def print_grid(grid: Grid[str], num_rows: int, num_cols: int):
    for r in range(num_rows):
        for c in range(num_cols):
            print(grid.get((r, c), "#"), end="")
        print()


def gather_pushed_tiles(
        grid: Grid[str],
        loc: GridPoint,
        move: str,
) -> list[GridPoint]:
    """
    Gather the locations of tiles that will be pushed by this move at
    this location in this grid; return those tile locations from closest
    to farthest.

    Assumes that this move would overlap a box tile.
    """
    move_offset = MOVE_OFFSETS[move]
    next_loc = add_points(loc, move_offset)

    # If pushing a box left/right (the simpler case)
    if move in "><":
        # Gather the group of box tiles we're pushing
        next_in_dir = next_loc
        pushed_tiles: list[GridPoint] = []
        while grid.get(next_in_dir) in BOX_OFFSETS.keys():
            pushed_tiles.append(next_in_dir)
            next_in_dir = add_points(next_in_dir, move_offset)

        # If moving into empty space, we're pushing the gathered tiles;
        # otherwise, we're blocked and pushing no tiles
        return pushed_tiles if next_in_dir in grid else []

    # If we're here, we're pushing a box up/down
    # NOTE Our vertical push could cause a chain reaction of boxes
    # pushing other boxes. Thus, we'll check each row from closest to
    # farthest for tiles that will be pushed; each row of pushed tile
    # positions will be appended to pushed_rows.

    # The box tile in front of us, and every tile it's connected to,
    # will be pushed
    pushed_rows = [
        [
            add_points(next_loc, box_offset)
            for box_offset in BOX_OFFSETS[grid[next_loc]]
        ],
    ]
    # Find the rest of the group of boxes we're pushing
    while True:
        # Each pushed box tile from the last row should push the tile in
        # front of it...
        next_row = {add_points(p, move_offset) for p in pushed_rows[-1]}
        # ...and the tiles that those tiles are connected to
        next_row |= {
            add_points(p, box_offset)
            for p in next_row
            for box_offset in BOX_OFFSETS.get(grid.get(p, "#"), [])
        }

        # If moving into a wall, we're blocked and pushing no tiles
        if any(p not in grid for p in next_row):
            return []

        # If moving into more boxes, their tiles will also be pushed
        if (next_tiles := [
            p for p in next_row
            if grid[p] in BOX_OFFSETS.keys()
        ]):
            pushed_rows.append(next_tiles)
        # Otherwise, we're done looking for boxes; gather the tiles from
        # every row and return them
        else:
            return [tile for row in pushed_rows for tile in row]


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2024 Day 15.
    """
    _year = 2024
    _day = 15

    separator = "\n\n"

    def _solve(self, raw_grid: list[str], moves: Iterable[str]) -> int:
        num_rows, num_cols = len(raw_grid), len(raw_grid[0])
        grid = parse_grid(raw_grid, ignore_chars="#")
        loc = next(k for k, v in grid.items() if v == "@")

        for move in moves:
            if self.debugging:
                from time import sleep
                print_grid(grid, num_rows, num_cols)
                self.debug()
                sleep(0.1)
                self.debug(f"Making move {move}")

            move_offset = MOVE_OFFSETS[move]
            # Do nothing if moving into a wall
            if (next_loc := add_points(loc, move_offset)) not in grid:
                continue

            # If pushing a box
            if grid[next_loc] in BOX_OFFSETS.keys():
                pushed_tiles = gather_pushed_tiles(grid, loc, move)
                # If this move doesn't push any tiles, cancel the move
                if not pushed_tiles:
                    continue

                # Push the tiles in the group from farthest to closest
                for p in reversed(pushed_tiles):
                    grid[add_points(p, move_offset)] = grid[p]
                    grid[p] = "."

            # Move the robot
            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc

        if self.debugging:
            print_grid(grid, num_rows, num_cols)

        return sum(
            100 * row + col
            for (row, col), char in grid.items()
            if char in "O["
        )

    @answer(1437174)
    def part_1(self) -> int:
        raw_grid = self.input[0].splitlines()
        moves = self.input[1].replace("\n", "")
        return self._solve(raw_grid, moves)

    @answer(1437468)
    def part_2(self) -> int:
        wide_table = str.maketrans({
            "#": "##",
            "O": "[]",
            ".": "..",
            "@": "@.",
        })
        raw_grid = self.input[0].translate(wide_table).splitlines()
        moves = self.input[1].replace("\n", "")
        return self._solve(raw_grid, moves)
