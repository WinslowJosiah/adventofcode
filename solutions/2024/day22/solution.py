# https://adventofcode.com/2024/day/22

from collections import Counter, deque
from itertools import pairwise

from ...base import IntSplitSolution, answer, slow


def next_secret(secret: int) -> int:
    # NOTE The technical name for this is an Xorshift random number
    # generator; the operations have been replaced with equivalent
    # bitwise operators, so the resemblance is clearer.
    secret = (secret ^ (secret << 6)) & 0xffffff
    secret = (secret ^ (secret >> 5)) & 0xffffff
    return (secret ^ (secret << 11)) & 0xffffff


class Solution(IntSplitSolution):
    """
    Solution for Advent of Code 2024 Day 22.
    """
    _year = 2024
    _day = 22

    @answer(21147129593)
    def part_1(self) -> int:
        total = 0
        for secret in self.input:
            # Generate this buyer's 2000th secret
            for _ in range(2000):
                secret = next_secret(secret)
            total += secret
        return total

    @answer(2445)
    @slow
    def part_2(self) -> int:
        # Each price-change sequence will have an associated profit from
        # the entire market of buyers
        market_profits: Counter[tuple[int, ...]] = Counter()

        def price(secret: int) -> int:
            return secret % 10

        for secret in self.input:
            prices = [price(secret)]
            # Generate 2000 of this buyer's secrets to convert to prices
            for _ in range(2000):
                secret = next_secret(secret)
                prices.append(price(secret))

            # The price changes will be a sliding window
            changes: deque[int] = deque(maxlen=4)
            assert changes.maxlen is not None
            # Each price-change sequence will have an associated profit
            # from this buyer
            buyer_profits: dict[tuple[int, ...], int] = {}
            # For each pair of prices (and thus, for each price change)
            for prev_price, curr_price in pairwise(prices):
                changes.append(curr_price - prev_price)
                if len(changes) >= changes.maxlen:
                    # If this price-change sequence wasn't seen before,
                    # associate it with the buyer's current price
                    buyer_profits.setdefault(tuple(changes), curr_price)
            # Add all possible buyer profits to the profit totals
            market_profits.update(buyer_profits)

        return max(market_profits.values())
