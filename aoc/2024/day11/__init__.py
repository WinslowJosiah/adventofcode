from collections import Counter
from collections.abc import Iterable


def blink_one_stone(stone: int) -> list[int]:
    """
    Simulate a stone changing (and possibly splitting) upon blinking.
    """
    # 0 is replaced with 1
    if not stone:
        return [1]
    # If the stone has an even number of digits
    elif not len(str_stone := str(stone)) % 2:
        # The left half and right half of the digits become new stones
        midpoint = len(str_stone) // 2
        return [int(str_stone[:midpoint]), int(str_stone[midpoint:])]
    # If no other rules apply
    else:
        # The stone is multiplied by 2024
        return [stone * 2024]


def blink_all_stones(stones: Counter[int]) -> Counter[int]:
    """
    Simulate a group of stones changing (and possibly splitting) upon
    blinking.
    """
    new_stones: Counter[int] = Counter()
    for stone, count in stones.items():
        for new_stone in blink_one_stone(stone):
            new_stones[new_stone] += count
    return new_stones


def aoc2024_day11_part1(lines: Iterable[str]) -> int:
    line = list(lines)[0]
    stones = Counter(map(int, line.split()))

    for _ in range(25):
        stones = blink_all_stones(stones)
    # Count the number of stones
    return sum(stones.values())


def aoc2024_day11_part2(lines: Iterable[str]) -> int:
    line = list(lines)[0]
    stones = Counter(map(int, line.split()))

    for _ in range(75):
        stones = blink_all_stones(stones)
    # Count the number of stones
    return sum(stones.values())


parts = (aoc2024_day11_part1, aoc2024_day11_part2)
