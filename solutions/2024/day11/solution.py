# https://adventofcode.com/2024/day/11

from collections import Counter
from collections.abc import Iterator

from ...base import IntSplitSolution, answer


def blink(stone: int) -> Iterator[int]:
    # 0 turns to 1
    if stone == 0:
        yield 1
        return

    # If the digit string can be split in half, it turns to both halves
    digits = str(stone)
    half_length, remainder = divmod(len(digits), 2)
    if remainder == 0:
        yield int(digits[:half_length])
        yield int(digits[half_length:])
        return

    # Any other number n turns to n * 2024
    yield stone * 2024
    return


class Solution(IntSplitSolution):
    """
    Solution for Advent of Code 2024 Day 11.
    """
    _year = 2024
    _day = 11

    separator = " "

    def _solve(self, blinks: int) -> int:
        # NOTE We can get away with only storing stone counts. Despite
        # the prompt saying "order is preserved", order does not matter.
        stones = Counter(self.input)

        for _ in range(blinks):
            new_stones: Counter[int] = Counter()
            for stone, count in stones.items():
                for new_stone in blink(stone):
                    new_stones[new_stone] += count
            stones = new_stones

        return stones.total()

    @answer(184927)
    def part_1(self) -> int:
        return self._solve(25)

    @answer(220357186726677)
    def part_2(self) -> int:
        return self._solve(75)
