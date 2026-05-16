# https://adventofcode.com/2024/day/9

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import batched, chain, repeat

from ...base import TextSolution, answer


type Block = int | None


def checksum_blocks(blocks: Iterable[Block]) -> int:
    return sum(
        address * block
        for address, block in enumerate(blocks)
        if block is not None
    )


class Solution(TextSolution):
    """
    Solution for Advent of Code 2024 Day 9.
    """
    _year = 2024
    _day = 9

    @answer(6366665108136)
    def part_1(self) -> int:
        assert len(self.input) % 2 == 1
        digits = map(int, self.input + "0")  # make last gap be 0
        # A disk is a list of blocks; a block is a file ID or None
        disk: list[Block] = []
        for file_id, (file_size, gap_size) in enumerate(batched(digits, 2)):
            disk.extend(repeat(file_id, file_size))
            disk.extend(repeat(None, gap_size))

        # The reader will scan backwards for files
        reader = len(disk) - 1
        # The writer will scan forwards for gaps
        writer = 0
        while True:
            # Find the next file block
            while (file_id := disk[reader]) is None:
                reader -= 1

            # Find the next gap before the file
            while writer < reader:
                if disk[writer] is None:
                    break
                writer += 1
            else:
                # Stop looping if no suitable gap is found
                break

            # Remove the file and move it to the gap
            disk[writer] = file_id
            disk[reader] = None

        return checksum_blocks(disk)

    @answer(6398065450842)
    def part_2(self) -> int:
        # NOTE A "chunk" is either a file (if its block value is an int)
        # or a gap (if its block value is None).
        @dataclass
        class Chunk:
            block: Block
            size: int

        assert len(self.input) % 2 == 1
        digits = map(int, self.input + "0")  # make last gap be 0
        # A disk is a list of chunks
        disk: list[Chunk] = []
        for file_id, (file_size, gap_size) in enumerate(batched(digits, 2)):
            disk.append(Chunk(file_id, file_size))
            disk.append(Chunk(None, gap_size))

        # NOTE The last chunk is a gap; the chunk before last is the
        # file with the largest file ID.
        max_file_id = disk[-2].block
        assert max_file_id is not None

        # The reader will scan backwards for files
        reader = len(disk) - 1
        for file_id in range(max_file_id, -1, -1):
            # Find the next file chunk
            while (file := disk[reader]).block != file_id:
                reader -= 1

            # The writer will scan forwards for gaps
            writer = 0
            # Find the next large enough gap before the file
            while writer < reader:
                if (
                    (gap := disk[writer]).block is None
                    and gap.size >= file.size
                ):
                    break
                writer += 1
            else:
                # Move on if no suitable gap is found
                continue

            # Remove the file and move it to the gap
            disk.insert(writer, file)
            reader += 1  # the insert shifts the index by 1
            disk[reader] = Chunk(None, file.size)
            # Reduce the size of the gap to account for the file
            gap.size -= file.size

        return checksum_blocks(
            chain.from_iterable(
                repeat(chunk.block, chunk.size) for chunk in disk
            )
        )
