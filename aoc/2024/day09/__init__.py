from collections.abc import Iterable
from typing import TypeAlias


Disk: TypeAlias = list[int | None]


def create_disk(disk_map: str) -> Disk:
    """
    Create a disk from a disk map.

    The disk will be created with no free space after the last file; the
    last block of the disk will be the block with the largest file ID.
    """
    disk: Disk = []
    file_id, free_space = 0, False
    for digit in disk_map:
        # Add file or free space to disk
        block = None if free_space else file_id
        disk.extend([block] * int(digit))
        # Move on to next file
        if free_space:
            file_id += 1
        # Next digit switches block type
        free_space = not free_space

    # Remove any trailing blocks of free space (just in case)
    while disk[-1] is None:
        disk.pop()
    return disk


def checksum_disk(disk: Disk) -> int:
    """
    Calculate checksum for disk.
    """
    return sum(
        i * (file_id or 0)
        for i, file_id in enumerate(disk)
    )


def aoc2024_day09_part1(lines: Iterable[str]) -> int:
    disk = create_disk(list(lines)[0])

    pointer = 0
    while True:
        # Find next block of free space
        try:
            pointer = disk.index(None, pointer)
        # If no blocks of free space were found
        except ValueError:
            # No file blocks need to be moved; return checksum
            return checksum_disk(disk)

        # Remove blocks of free space from end of disk
        while (block := disk.pop()) is None:
            # Stop if length of disk gets too small
            if pointer >= len(disk):
                break
        # Once a file block has been found
        else:
            # Place it in this block of free space
            disk[pointer] = block


def aoc2024_day09_part2(lines: Iterable[str]) -> int:
    disk = create_disk(list(lines)[0])

    # Find first block of free space
    try:
        first_space_start = disk.index(None)
    # If there is no free space
    except ValueError:
        # There's no need to defragment; return checksum
        return checksum_disk(disk)

    # Initialize right pointer
    right_pointer = len(disk) - 1
    # NOTE The last block of the disk will contain the largest file ID.
    last_file_id = disk[right_pointer]
    assert last_file_id is not None

    # For each file ID from the last file to 0
    for file_id in range(last_file_id, -1, -1):
        # Scan to this file
        while disk[right_pointer] != file_id:
            right_pointer -= 1
        # Get file metadata
        file_length = 0
        while right_pointer >= 0 and disk[right_pointer] == file_id:
            file_length += 1
            right_pointer -= 1
        file_start = right_pointer + 1

        # We will try to find enough free space on the left
        left_pointer = first_space_start
        while left_pointer <= right_pointer:
            # Count free space here
            space_start, space_length = left_pointer, 0
            while left_pointer < len(disk) and disk[left_pointer] is None:
                space_length += 1
                left_pointer += 1
            # If there is enough free space
            if file_length <= space_length:
                # Move the file here
                for k in range(file_length):
                    disk[space_start + k] = file_id
                    disk[file_start + k] = None
                # Stop trying to find free space
                break

            # Find next block of free space
            try:
                left_pointer = disk.index(None, left_pointer)
            # If no blocks of free space were found
            except ValueError:
                # Stop trying to find free space
                break

        # The location of the first block of free space might've changed
        # NOTE Because we've already made sure the disk has at least one
        # block of free space, this list.index() call will never fail.
        first_space_start = disk.index(None, first_space_start)

    # Return checksum (finally!)
    return checksum_disk(disk)


parts = (aoc2024_day09_part1, aoc2024_day09_part2)
