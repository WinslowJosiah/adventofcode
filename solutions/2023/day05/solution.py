# https://adventofcode.com/2023/day/5

from collections.abc import Generator
from itertools import batched

from ...base import StrSplitSolution, answer


# mask, offset
type Transformation = tuple[range, int]


def parse_range(line: str) -> Transformation:
    dest_start, source_start, size = map(int, line.split())
    return range(source_start, source_start + size), dest_start - source_start


def parse_transformations(block: str) -> list[Transformation]:
    # NOTE The first line of a block is its category; the rest are
    # ranges.
    return [parse_range(l) for l in block.splitlines()[1:]]


def transform_number(num: int, transformations: list[Transformation]) -> int:
    for mask, offset in transformations:
        if num in mask:
            return num + offset
    return num


def transform_range(
        base: range,
        transformations: list[Transformation],
) -> Generator[range]:
    for mask, offset in transformations:
        # If this range overlaps with base, use its mask and offset
        if base.start < mask.stop and mask.start < base.stop:
            break
    else:
        # If no mask overlapped with base, yield only the unchanged base
        yield base
        return

    # Apply transformation to segment within mask
    start = max(base.start, mask.start)
    stop = min(base.stop, mask.stop)
    yield range(start + offset, stop + offset)
    # Apply transformations to segment before mask
    if base.start < mask.start:
        yield from transform_range(
            range(base.start, mask.start),
            transformations,
        )
    # Apply transformations to segment after mask
    if mask.stop < base.stop:
        yield from transform_range(
            range(mask.stop, base.stop),
            transformations,
        )


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 5.
    """
    _year = 2023
    _day = 5

    separator = "\n\n"

    @answer(1181555926)
    def part_1(self) -> int:
        raw_seeds, *blocks = self.input
        seeds = map(int, raw_seeds.removeprefix("seeds:").split())

        transformation_groups = [parse_transformations(b) for b in blocks]
        locations: list[int] = []
        for seed in seeds:
            for transformations in transformation_groups:
                seed = transform_number(seed, transformations)
            locations.append(seed)

        return min(locations)

    @answer(37806486)
    def part_2(self) -> int:
        raw_seeds, *blocks = self.input
        seeds = map(int, raw_seeds.removeprefix("seeds:").split())
        seed_ranges = [
            range(start, start + size)
            for start, size in batched(seeds, 2)
        ]

        transformation_groups = [parse_transformations(b) for b in blocks]
        location_ranges: list[range] = []
        for seed_range in seed_ranges:
            ranges = [seed_range]
            for transformations in transformation_groups:
                ranges = [
                    result
                    for r in ranges
                    for result in transform_range(r, transformations)
                ]
            location_ranges.extend(ranges)

        return min(r.start for r in location_ranges)
