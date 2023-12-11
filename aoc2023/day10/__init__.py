from collections.abc import Iterable


# Simple Vector-like class
class Vector:
    def __init__(self, *args: int):
        self.values = args

    def __iter__(self):
        return self.values.__iter__()

    def __add__(self, other: "Vector"):
        return self.__class__(*map(lambda a, b: a + b, self, other))

    def __mul__(self, other: int):
        return self.__class__(*(v * other for v in self))

    __radd__ = __add__
    __rmul__ = __mul__

    def __neg__(self):
        return self.__mul__(-1)

    def __eq__(self, other: object):
        if not isinstance(other, Vector):
            return False
        return self.values.__eq__(other.values)

    def __lt__(self, other: "Vector"):
        return self.values.__lt__(other.values)

    def __hash__(self):
        return self.values.__hash__()

    def __str__(self):
        return self.values.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self))})"


def aoc2023_day10_part1(lines: Iterable[str]) -> int:
    # This is a list of valid offsets
    offsets = [Vector(-1, 0), Vector(0, -1), Vector(0, 1), Vector(1, 0)]
    # This dict maps pipe characters to the offsets they connect to
    pipe_connections = {
        "|": [Vector(-1, 0), Vector(1, 0)],
        "-": [Vector(0, -1), Vector(0, 1)],
        "L": [Vector(-1, 0), Vector(0, 1)],
        "J": [Vector(-1, 0), Vector(0, -1)],
        "7": [Vector(0, -1), Vector(1, 0)],
        "F": [Vector(0, 1), Vector(1, 0)],
    }

    tiles = list(lines)
    height = len(tiles)
    width = len(tiles[0])

    # Find the starting position of the animal
    for row, line in enumerate(tiles):
        col = line.find("S")
        if col >= 0:
            start_pos = Vector(row, col)
            break
    else:
        # If starting position was not found, the puzzle is invalid
        raise RuntimeError("Starting position was not found")

    # Find a tile that connects to the starting position
    for offset in offsets:
        # Get position at offset
        pos = start_pos + offset
        row, col = pos
        # Skip if position is out of bounds
        if not (0 <= row < height):
            continue
        if not (0 <= col < width):
            continue

        # Skip if position has no pipe
        if tiles[row][col] not in pipe_connections:
            continue

        # If pipe connects backwards to starting position
        if -offset in pipe_connections[tiles[row][col]]:
            # This position is a connection
            next_pos = pos
            break
    else:
        # If there is no connecting tile, the puzzle is invalid
        raise RuntimeError("No tiles connect to starting position")

    # Choose one connected tile to start path on
    last_pos, pos = start_pos, next_pos
    path_length = 1
    # Until the path loops back to the starting position
    while pos != start_pos:
        row, col = pos
        tile = tiles[row][col]
        # Find next connection going out from this tile
        # NOTE: This assumes the tile is a pipe; thus, we can use the
        # mapping of connections defined before.
        for offset in pipe_connections[tile]:
            next_pos = pos + offset
            # Only go to next tile if it's different from the last tile
            if next_pos != last_pos:
                break
        else:
            # If there is no next tile, the puzzle is invalid
            raise RuntimeError("Loop stops at position:", pos)

        # Move forward to next tile
        last_pos, pos = pos, next_pos
        path_length += 1

    # The farthest tile from the start is half the path length away
    return path_length // 2


def aoc2023_day10_part2(lines: Iterable[str]) -> int:
    import re

    # This is a list of valid offsets
    offsets = [Vector(-1, 0), Vector(0, -1), Vector(0, 1), Vector(1, 0)]
    # This dict maps pipe characters to the offsets they connect to
    pipe_connections = {
        "|": [Vector(-1, 0), Vector(1, 0)],
        "-": [Vector(0, -1), Vector(0, 1)],
        "L": [Vector(-1, 0), Vector(0, 1)],
        "J": [Vector(-1, 0), Vector(0, -1)],
        "7": [Vector(0, -1), Vector(1, 0)],
        "F": [Vector(0, 1), Vector(1, 0)],
    }
    # This regex matches a vertical "boundary" in the tile diagram
    boundary_regex = re.compile(r"\||F-*J|L-*7")

    # NOTE: Here, the tiles are a list of lists of tiles, instead of a
    # list of string lines, because I need to be able to modify
    # individual tiles.
    tiles = list(map(list, lines))
    height = len(tiles)
    width = len(tiles[0])

    # Find the starting position of the animal
    for row, line in enumerate(tiles):
        try:
            # Find the index of the starting position
            col = line.index("S")
        except ValueError:
            # Skip line if starting position was not found yet
            continue
        else:
            # End loop if starting position was found
            start_pos = Vector(row, col)
            break
    else:
        # If starting position was not found, the puzzle is invalid
        raise RuntimeError("Starting position was not found")

    # Find a tile that connects to the starting position
    next_pos = None
    start_offsets: list[Vector] = []
    for offset in offsets:
        # Get position at offset
        pos = start_pos + offset
        row, col = pos
        # Skip if position is out of bounds
        if not (0 <= row < height):
            continue
        if not (0 <= col < width):
            continue

        # Skip if position has no pipe
        if tiles[row][col] not in pipe_connections:
            continue

        # If pipe connects backwards to starting position
        if -offset in pipe_connections[tiles[row][col]]:
            # This position is a connection
            next_pos = pos
            start_offsets.append(offset)

    if not start_offsets:
        # If there is no connecting tile, the puzzle is invalid
        raise RuntimeError("No tiles connect to starting position")
    assert next_pos is not None  # This makes the type checker happy

    # NOTE: To assist in finding tiles inside and outside of the loop,
    # we change the tile at its starting position to its corresponding
    # pipe.
    row, col = start_pos
    tiles[row][col] = next(
        char
        for char, connection_offsets in pipe_connections.items()
        if start_offsets == connection_offsets
    )

    # Choose one connected tile to start path on
    tiles_on_loop: set[Vector] = set([start_pos])
    last_pos, pos = start_pos, next_pos
    # Until the path loops back to the starting position
    while pos != start_pos:
        row, col = pos
        tile = tiles[row][col]
        # Find next connection going out from this tile
        # NOTE: This assumes the tile is a pipe; thus, we can use the
        # mapping of connections defined before.
        for offset in pipe_connections[tile]:
            next_pos = pos + offset
            # Only go to next tile if it's different from the last tile
            if next_pos != last_pos:
                break
        else:
            # If there is no next tile, the puzzle is invalid
            raise RuntimeError("Loop stops at position:", pos)

        # Move forward to next tile
        tiles_on_loop.add(pos)
        last_pos, pos = pos, next_pos

    # NOTE: To assist in finding tiles inside and outside of the loop,
    # we remove all tiles that are not on the loop itself.
    for row, line in enumerate(tiles):
        for col, tile in enumerate(line):
            if Vector(row, col) in tiles_on_loop:
                continue
            tiles[row][col] = "."

    # NOTE: We will determine which tiles are inside or outside of the
    # loop using the even-odd rule. Basically, we will scan each row
    # horizontally, and we will consider the "tile" before the start of
    # the row to be "outside". Then, each time we cross a boundary
    # (either |, F-J, or L-7), the tiles change from being "outside" to
    # "inside", and vice versa.
    inside_count = 0
    for line in tiles:
        line_str = "".join(line)
        # Split the line into sections based on vertical boundaries
        sections = boundary_regex.split(line_str)
        # The ground tiles in the odd-numbered sections are "inside"
        inside_count += sum(
            section.count(".")
            for section in sections[1::2]
        )

    # Return the count of inside tiles (finally!)
    return inside_count


parts = (aoc2023_day10_part1, aoc2023_day10_part2)
