from collections.abc import Iterable


def aoc2023_day05_part1(lines: Iterable[str]) -> int:
    def apply_mappings(
            n: int,
            mappings: dict[tuple[int, int], int],
    ) -> int:
        """
        Apply a set of mappings to a number `n`.

        The first mapping where `n` is within the correct range will be
        applied, and the result of the mapping will be returned; if no
        mapping is applied, `n` will be returned as is.
        """
        for (src_start, src_end), diff in mappings.items():
            if src_start <= n < src_end:
                return n + diff
        return n

    line_iter = iter(lines)
    # Extract seed IDs from first line
    seeds_line = next(line_iter)
    _, seeds_str = seeds_line.split(": ")
    category_ids = list(map(int, seeds_str.split()))
    # Skip next blank line
    assert not next(line_iter)

    # Step through each category
    for _ in line_iter:
        # NOTE: The first line we come across will be a human-readable
        # description of the category (which we don't care about). The
        # lines afterwards, up until the first blank line, are the
        # mappings for this category.

        # Each mapping will be stored in a mapping (ironically)
        mappings: dict[tuple[int, int], int] = {}
        # This will store two pieces of information:
        # 1. The endpoints of the source range, as a tuple (key)
        # 2. The difference between the source range and the destination
        # range (value)

        # Go through lines to create mappings
        for line in line_iter:
            # Stop when a blank line is reached
            if not line:
                break
            # Extract numbers from mapping line
            dest, src, range_len = map(int, line.split())
            # Store relevant range information
            mappings[(src, src + range_len)] = dest - src

        # I could've used map() to apply the mappings, but that would be
        # slightly slower. It would've been funny, though.
        category_ids = [
            apply_mappings(id, mappings)
            for id in category_ids
        ]

    # Return the minimum ID in the current category
    return min(category_ids)


def aoc2023_day05_part2(lines: Iterable[str]) -> int:
    from itertools import batched, chain

    def apply_mappings(
            r: tuple[int, int],
            mappings: dict[tuple[int, int], int],
    ) -> set[tuple[int, int]]:
        """
        Apply a set of mappings to a range `r`.

        The range will be split into one or more ranges, based on how
        elements inside the range are mapped.
        """
        # Input range hasn't been mapped yet
        mapped: set[tuple[int, int]] = set()
        unmapped: set[tuple[int, int]] = set([r])

        # Go through each mapping
        for (src_start, src_end), diff in mappings.items():
            new_unmapped: set[tuple[int, int]] = set()
            # For each range that hasn't been mapped yet
            for (range_start, range_end) in unmapped:
                # If the current range is outside of the mapping range
                if range_end <= src_start or range_start >= src_end:
                    # The current range doesn't change
                    new_unmapped.add((range_start, range_end))
                    continue

                # If we're here, the ranges overlap

                # If the current range starts before the mapping range
                if range_start < src_start:
                    # The part before the mapping range doesn't change
                    new_unmapped.add((range_start, src_start))

                # If the current range ends after the mapping range
                if src_end < range_end:
                    # The part after the mapping range doesn't change
                    new_unmapped.add((src_end, range_end))

                # Find endpoints of overlapping range
                overlap_start = max(range_start, src_start)
                overlap_end = min(range_end, src_end)
                # If the overlapping range is not empty
                if overlap_start < overlap_end:
                    # Apply the mapping to this range
                    mapped.add((overlap_start + diff, overlap_end + diff))

            # There is now a new set of unmapped ranges
            unmapped = new_unmapped

        # Return all ranges, whether mapped or unmapped
        return mapped | unmapped

    line_iter = iter(lines)
    # Extract seed IDs from first line
    seeds_line = next(line_iter)
    _, seeds_str = seeds_line.split(": ")

    seed_numbers = map(int, seeds_str.split())
    # The way we calculate the category IDs is different now.
    # 1. We must step through the seed numbers two at a time, and use
    # the ranges of category IDs defined by those pairs.
    # 2. Because storing all the category IDs would take too much time
    # and space (they get BIG), we instead store them as the endspoints
    # of ranges, as tuples.
    category_ranges: list[tuple[int, int]] = [
        (range_start, range_start + range_len)
        for (range_start, range_len) in batched(seed_numbers, 2)
    ]

    # Skip next blank line
    assert not next(line_iter)

    # Step through each category
    for _ in line_iter:
        # NOTE: The first line we come across will be a human-readable
        # description of the category (which we don't care about). The
        # lines afterwards, up until the first blank line, are the
        # mappings for this category.

        mappings: dict[tuple[int, int], int] = {}
        # Go through lines to create mappings
        for line in line_iter:
            # Stop when a blank line is reached
            if not line:
                break
            # Extract numbers from mapping line
            dest, src, range_len = map(int, line.split())
            # Store relevant range information
            mappings[(src, src + range_len)] = dest - src

        # Apply the mappings to each category range
        category_ranges = list(chain.from_iterable(
            apply_mappings(category_range, mappings)
            for category_range in category_ranges
        ))

    # Return minimum starting point in the current category's ranges
    return min(r[0] for r in category_ranges)


parts = (aoc2023_day05_part1, aoc2023_day05_part2)
