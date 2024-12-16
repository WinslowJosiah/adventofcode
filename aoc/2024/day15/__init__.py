from collections import defaultdict
from collections.abc import Iterable
from typing import TypeAlias


# NOTE I'm using complex numbers to store positions and offsets, because
# it's easier than juggling items in tuples. If we need each individual
# coordinate, however, they should be explicitly converted to ints.
Grid: TypeAlias = defaultdict[complex, str]
OFFSETS: dict[str, complex] = {
    ">": 1 + 0j, "<": -1 + 0j, "v": 1j, "^": -1j,
}
WIDE_TILES = {".": "..", "#": "##", "O": "[]"}


def aoc2024_day15_part1(lines: Iterable[str]) -> int:
    line_iter = iter(lines)
    # Compile the grid until the first blank line
    # NOTE We're using complex numbers to store positions and offsets,
    # because it's easier than juggling items in tuples.
    grid: Grid = defaultdict(lambda: "#")
    robot: complex | None = None
    for y, row in enumerate(line_iter):
        if not row:
            break
        for x, tile in enumerate(row):
            pos = x + y * 1j
            # If the robot was found
            if tile == "@":
                # Keep track of it, and empty its starting position
                robot, tile = pos, "."
            # Store the tile
            grid[pos] = tile
    assert robot is not None
    # The rest of the lines are the robot's movements
    movements = "".join(line_iter)

    # The robot will attempt all of the movements
    for movement in movements:
        offset = OFFSETS.get(movement, 0j)
        new_robot = robot + offset

        new_robot_tile = grid[new_robot]
        # If robot would run into a wall
        if new_robot_tile == "#":
            # Don't move the robot
            continue
        # If robot would run into a box
        elif new_robot_tile == "O":
            # Check space in front of all boxes being pushed
            box = new_robot
            while (tile := grid[box]) == "O":
                box += offset
            # If boxes would be pushed into a wall
            if tile == "#":
                # Don't move the boxes or the robot
                continue

            # Push the boxes
            # HACK Technically we're not pushing the boxes; we're
            # teleporting the front box to the back. Same difference!
            grid[box], grid[new_robot] = grid[new_robot], tile

        # Move the robot
        robot = new_robot

    # Calculate the sum of the boxes' GPS coordinates
    return sum(
        100 * int(pos.imag) + int(pos.real)
        for pos, tile in grid.items()
        if tile == "O"
    )


def aoc2024_day15_part2(lines: Iterable[str]) -> int:
    from collections import deque

    WIDE_BOX = WIDE_TILES["O"]

    line_iter = iter(lines)
    # Compile the grid until the first blank line
    # NOTE We're using complex numbers to store positions and offsets,
    # because it's easier than juggling items in tuples.
    grid: defaultdict[complex, str] = defaultdict(lambda: "#")
    robot: complex | None = None
    for y, row in enumerate(line_iter):
        if not row:
            break
        for x, tile in enumerate(row):
            # NOTE We multiply x by 2 because the grid is twice as wide.
            pos = x * 2 + y * 1j
            # If the robot was found
            if tile == "@":
                # Keep track of it, and empty its starting position
                robot, tile = pos, "."
            # Store the "wide tile"
            for w, wide_tile in enumerate(
                WIDE_TILES.get(tile, WIDE_TILES["."])
            ):
                grid[pos + w] = wide_tile
    assert robot is not None
    # The rest of the lines are the robot's movements
    movements = "".join(line_iter)

    # The robot will attempt all of the movements
    for movement in movements:
        offset = OFFSETS.get(movement, 0j)
        new_robot = robot + offset

        new_robot_tile = grid[new_robot]
        robot_is_pushing = new_robot_tile in WIDE_BOX
        # If robot would run into a wall
        if new_robot_tile == "#":
            # Don't move the robot
            continue
        # If robot would run into a box from the left or right
        elif robot_is_pushing and movement in "<>":
            # Check space in front of all the boxes being pushed
            box = new_robot
            while (tile := grid[box]) in WIDE_BOX:
                box += offset
            # If boxes would be pushed into a wall
            if tile == "#":
                # Don't move the boxes or the robot
                continue

            # Push the boxes
            while box != new_robot:
                grid[box] = grid[box - offset]
                box -= offset
            grid[new_robot] = tile
        # If robot would run into a box from the top or bottom
        # NOTE This is a separate case because it's way more
        # complicated. Boxes are twice as wide, so the group of boxes
        # that gets pushed may have a complex shape.
        elif robot_is_pushing and movement in "^v":
            # HACK I'm storing the positions of each box to move as the
            # keys of a dict (where the value doesn't matter). This way,
            # I can preserve the order, and the box positions will be
            # unique.
            boxes_to_push: dict[complex, None] = {}
            # Get the leftmost position of this box
            box = new_robot
            while grid[box] != WIDE_BOX[0]:
                box -= 1
            # We will find the boxes to push with a breadth-first search
            box_queue = deque([box])
            while box_queue:
                box = box_queue.popleft()
                # This box will be pushed
                boxes_to_push[box] = None
                # For each position in front of this box
                for w in range(len(WIDE_BOX)):
                    in_front_of_box = box + w + offset
                    # If this box would be pushed into a wall
                    if grid[in_front_of_box] == "#":
                        # Don't push any boxes, and stop trying to
                        box_queue.clear()
                        boxes_to_push.clear()
                        break
                    # If this box would be pushed into another box
                    elif grid[in_front_of_box] in WIDE_BOX:
                        # Get the leftmost position of this box
                        while grid[in_front_of_box] != WIDE_BOX[0]:
                            in_front_of_box -= 1
                        # This box will be pushed
                        boxes_to_push[in_front_of_box] = None
                        # We will consider which boxes this box pushes
                        box_queue.append(in_front_of_box)
            # If no boxes would be pushed
            if not boxes_to_push:
                # Don't move the robot
                continue

            # Push the boxes
            # NOTE The boxes were added in order from back to front. To
            # ensure the boxes in front get pushed into empty space
            # before the boxes in back, we iterate through them in order
            # from front to back.
            for box in reversed(boxes_to_push):
                for w in range(len(WIDE_BOX)):
                    grid[box + w + offset], grid[box + w] = (
                        grid[box + w], grid[box + w + offset]
                    )

        # Move the robot
        robot = new_robot

    # Calculate the sum of the boxes' GPS coordinates
    return sum(
        100 * int(pos.imag) + int(pos.real)
        for pos, char in grid.items()
        if char == WIDE_BOX[0]
    )


parts = (aoc2024_day15_part1, aoc2024_day15_part2)
