from collections.abc import Iterable


def next_secret(secret: int) -> int:
    """
    Generate the next secret number, given an initial (nonzero) secret
    number.
    """
    # NOTE This is equivalent to the specified process. In fact, this is
    # actually a 24-bit xorshift PRNG, which is neat.
    secret = (secret ^ (secret << 6)) & 0xffffff
    secret = (secret ^ (secret >> 5)) & 0xffffff
    return (secret ^ (secret << 11)) & 0xffffff


def aoc2024_day22_part1(lines: Iterable[str]) -> int:
    total = 0
    for secret in map(int, lines):
        # Get the 2000th secret number
        for _ in range(2000):
            secret = next_secret(secret)
        total += secret
    return total


def aoc2024_day22_part2(lines: Iterable[str]) -> int:
    from collections import Counter, deque

    profits: Counter[tuple[int, ...]] = Counter()

    for secret in map(int, lines):
        # Last price for this buyer
        last_price = secret % 10
        # Last 4 price differences
        last_diffs: deque[int] = deque(maxlen=4)
        assert last_diffs.maxlen is not None
        # Profit for each collection of price differences
        diffs_to_profit: dict[tuple[int, ...], int] = {}

        # For this buyer's next 2000 secret numbers
        for _ in range(2000):
            secret = next_secret(secret)
            price = secret % 10
            last_diffs.append(price - last_price)
            last_price = price

            # If there are at least enough price differences to use
            if len(last_diffs) >= last_diffs.maxlen:
                # These differences correspond to this price
                # NOTE dict.setdefault() only stores a value if the key
                # hasn't been seen yet. So if we see the same price
                # differences again, this will do nothing.
                diffs_to_profit.setdefault(tuple(last_diffs), price)

        # Count profits from this buyer for all possible collections of
        # price difference
        profits.update(diffs_to_profit)

    return max(profits.values())


parts = (aoc2024_day22_part1, aoc2024_day22_part2)
