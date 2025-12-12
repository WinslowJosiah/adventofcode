# https://adventofcode.com/2025/day/10

from collections.abc import Sequence, Set
from collections import defaultdict
from functools import cache
from itertools import combinations

from ...base import StrSplitSolution, answer


type Wiring = Set[int]
type Presses = tuple[Wiring, ...]


def parse_machine(line: str) -> tuple[Wiring, Sequence[Wiring], list[int]]:
    raw_indicators, *raw_buttons, raw_joltages = (
        part[1:-1] for part in line.split()
    )

    indicators = {i for i, ch in enumerate(raw_indicators) if ch == "#"}
    buttons = [
        set(map(int, raw_button.split(",")))
        for raw_button in raw_buttons
    ]
    joltages = list(map(int, raw_joltages.split(",")))
    return indicators, buttons, joltages


def valid_patterns(buttons: Sequence[Wiring]) -> dict[Wiring, list[Presses]]:
    """
    Precompute all possible indicator patterns and the combinations of
    button presses that produce them.
    """
    patterns: dict[Wiring, list[Presses]] = defaultdict(list)
    for num_presses in range(len(buttons) + 1):
        for presses in combinations(buttons, num_presses):
            pattern: Wiring = set()
            for button in presses:
                pattern ^= button
            patterns[frozenset(pattern)].append(presses)
    return patterns


def configure_indicators(
        indicators: Wiring,
        patterns: dict[Wiring, list[Presses]],
) -> int | None:
    presses_list = patterns.get(frozenset(indicators), [])
    return min((len(presses) for presses in presses_list), default=None)


def configure_joltages(
        joltages: list[int],
        patterns: dict[Wiring, list[Presses]],
) -> int | None:
    # NOTE Pressing a button twice does nothing to the indicator lights,
    # but increases some joltages by 2. So we can configure the joltages
    # by first reaching the corresponding indicator state, then pressing
    # some other set of buttons twice to make up the difference.
    # Idea from u/tenthmascot: https://redd.it/1pk87hl
    @cache
    def get_min_presses(target: tuple[int, ...]) -> int | None:
        # No button presses are needed to reach zero joltage
        if not any(target):
            return 0

        # We must turn on the indicators with odd joltage levels
        indicators = frozenset(
            i for i, joltage in enumerate(target) if joltage % 2 == 1
        )
        result = None
        for presses in patterns[indicators]:
            # Simulate button presses to reach indicator state
            target_after = list(target)
            for button in presses:
                for joltage_index in button:
                    target_after[joltage_index] -= 1
            # Skip if any levels become negative
            if any(joltage < 0 for joltage in target_after):
                continue

            # All new target levels are even; calculate min presses to
            # reach half the target levels
            half_target = tuple(joltage // 2 for joltage in target_after)
            num_half_target_presses = get_min_presses(half_target)
            if num_half_target_presses is None:
                continue
            # We can reach the target by reaching the half-target twice;
            # add twice the half-target presses to the initial ones
            num_presses = len(presses) + 2 * num_half_target_presses

            # Update minimum presses count
            if result is None:
                result = num_presses
            else:
                result = min(result, num_presses)

        return result

    return get_min_presses(tuple(joltages))


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 10.
    """
    _year = 2025
    _day = 10

    @answer((542, 20871))
    def solve(self) -> tuple[int, int]:
        num_indicator_presses, num_joltage_presses = 0, 0
        for line in self.input:
            indicators, buttons, joltages = parse_machine(line)
            patterns = valid_patterns(buttons)

            indicator_result = configure_indicators(indicators, patterns)
            assert indicator_result is not None
            num_indicator_presses += indicator_result

            joltage_result = configure_joltages(joltages, patterns)
            assert joltage_result is not None
            num_joltage_presses += joltage_result

        return num_indicator_presses, num_joltage_presses
