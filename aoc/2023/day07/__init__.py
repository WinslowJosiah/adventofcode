from collections.abc import Iterable


def aoc2023_day07_part1(lines: Iterable[str]) -> int:
    from collections import Counter
    from enum import IntEnum

    class HandType(IntEnum):
        HIGH_CARD = 1
        ONE_PAIR = 2
        TWO_PAIR = 3
        THREE_OF_A_KIND = 4
        FULL_HOUSE = 5
        FOUR_OF_A_KIND = 6
        FIVE_OF_A_KIND = 7

    def get_hand_type(cards: str) -> HandType:
        """
        Find the "hand type" of a hand of 5 cards (represented as a
        `str` of card values).
        """
        card_counts = Counter(cards)

        # 5 matching cards = FIVE OF A KIND
        if any(count == 5 for count in card_counts.values()):
            return HandType.FIVE_OF_A_KIND

        # 4 matching cards = FOUR OF A KIND
        if any(count == 4 for count in card_counts.values()):
            return HandType.FOUR_OF_A_KIND

        if any(count == 3 for count in card_counts.values()):
            # 3 matching cards, and two unique card values = FULL HOUSE
            if len(card_counts) == 2:
                return HandType.FULL_HOUSE
            # 3 matching cards, and not a full house = THREE OF A KIND
            return HandType.THREE_OF_A_KIND

        # Count the number of pairs
        pair_count = len([
            count for count in card_counts.values()
            if count == 2
        ])
        # Two pairs = TWO PAIR
        if pair_count == 2:
            return HandType.TWO_PAIR
        # One pair = ONE PAIR
        if pair_count == 1:
            return HandType.ONE_PAIR

        # No other better type = HIGH CARD
        return HandType.HIGH_CARD

    # Gather the list of hands and bids
    hands: dict[str, int] = {}
    for line in lines:
        hand, bid = line.split()
        hands[hand] = int(bid)

    # Sort the hands in ascending order by rank
    hands = dict(sorted(
        hands.items(),
        key=lambda hands_item: (
            # First, sort by hand type...
            get_hand_type(hands_item[0]),
            # ...then, sort by each card value in order
            ["23456789TJQKA".index(card) for card in hands_item[0]],
        ),
    ))

    # The winnings are the sum of the rank-bid product of each hand
    return sum(
        rank * bid
        for rank, bid in enumerate(hands.values(), 1)
    )


def aoc2023_day07_part2(lines: Iterable[str]) -> int:
    from collections import Counter
    from enum import IntEnum

    class HandType(IntEnum):
        HIGH_CARD = 1
        ONE_PAIR = 2
        TWO_PAIR = 3
        THREE_OF_A_KIND = 4
        FULL_HOUSE = 5
        FOUR_OF_A_KIND = 6
        FIVE_OF_A_KIND = 7

    def get_hand_type(cards: str) -> HandType:
        """
        Find the "hand type" of a hand of 5 cards (represented as a
        `str` of card values).
        """
        card_counts = Counter(cards)

        # Because of the existence of jokers, we need to deal with the
        # card counts a bit differently. First, we count the number of
        # jokers, and remove the jokers from our card counter.
        joker_count = card_counts.pop("J", 0)
        # If we now have no cards, we have a FIVE OF A KIND of jokers
        if not card_counts:
            return HandType.FIVE_OF_A_KIND

        # 5 matching cards = FIVE OF A KIND
        if any(count == 5 - joker_count for count in card_counts.values()):
            return HandType.FIVE_OF_A_KIND

        # 4 matching cards = FOUR OF A KIND
        if any(count == 4 - joker_count for count in card_counts.values()):
            return HandType.FOUR_OF_A_KIND

        if any(count == 3 - joker_count for count in card_counts.values()):
            # 3 matching cards, and two unique card values = FULL HOUSE
            if len(card_counts) == 2:
                return HandType.FULL_HOUSE
            # 3 matching cards, and not a full house = THREE OF A KIND
            return HandType.THREE_OF_A_KIND

        # The jokers require us to count pairs creatively
        pair_count = 0
        jokers_left = joker_count
        # We consider the cases where 0 jokers and 1 joker are in a pair
        # NOTE: 2 jokers can't be in a pair by themselves; they'd have
        # been detected as one of the better hand types instead.
        for jokers_in_pair in range(2):
            # For each count of a certain card
            for count in card_counts.values():
                # If this card forms a pair with the jokers we have left
                if (
                    count == 2 - jokers_in_pair
                    and jokers_left >= jokers_in_pair
                ):
                    # This counts as 1 pair
                    pair_count += 1
                    # Remove the jokers we used in the pair
                    jokers_left -= jokers_in_pair

        # Two pairs = TWO PAIR
        if pair_count == 2:
            return HandType.TWO_PAIR
        # One pair = ONE PAIR
        if pair_count == 1:
            return HandType.ONE_PAIR

        # No other better type = HIGH CARD
        return HandType.HIGH_CARD

    # Gather the list of hands and bids
    hands: dict[str, int] = {}
    for line in lines:
        hand, bid = line.split()
        hands[hand] = int(bid)

    # Sort the hands in ascending order by rank
    hands = dict(sorted(
        hands.items(),
        key=lambda hands_item: (
            # First, sort by hand type...
            get_hand_type(hands_item[0]),
            # ...then, sort by each card value in order
            ["J23456789TQKA".index(card) for card in hands_item[0]],
        ),
    ))

    # The winnings are the sum of the rank-bid product of each hand
    return sum(
        rank * bid
        for rank, bid in enumerate(hands.values(), 1)
    )


parts = (aoc2023_day07_part1, aoc2023_day07_part2)
