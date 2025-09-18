# https://adventofcode.com/2023/day/20

from abc import ABC, abstractmethod
from collections import Counter, deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import count
from math import lcm

from ...base import StrSplitSolution, answer


@dataclass
class BaseModule(ABC):
    name: str
    targets: list[str]

    @abstractmethod
    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        ...


@dataclass
class FlipFlopModule(BaseModule):
    _state: bool = field(default=False, init=False, repr=False)

    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        if is_high_pulse:
            return None
        self._state = not self._state
        return self._state


@dataclass
class ConjunctionModule(BaseModule):
    _source_states: dict[str, bool] = field(
        default_factory=dict[str, bool],
        init=False,
        repr=False,
    )

    @property
    def sources(self) -> list[str]:
        return list(self._source_states.keys())

    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        self._source_states[source] = is_high_pulse
        return not all(self._source_states.values())

    def register_source(self, source: str) -> None:
        self._source_states[source] = False


class Computer:
    def __init__(self, lines: list[str]) -> None:
        raw_modules = [line.split(" -> ") for line in lines]

        # Initialize modules and set their targets
        self.modules: dict[str, BaseModule] = {}
        for raw_source, raw_targets in raw_modules:
            targets = raw_targets.split(", ")
            if raw_source == "broadcaster":
                self.broadcaster_targets = targets
                continue

            module_type, name = raw_source[0], raw_source[1:]
            if module_type == "%":
                self.modules[name] = FlipFlopModule(name, targets)
            elif module_type == "&":
                self.modules[name] = ConjunctionModule(name, targets)

        # Register sources for conjunction modules
        for source_name, source_module in self.modules.items():
            for target_name in source_module.targets:
                target_module = self.modules.get(target_name)
                if isinstance(target_module, ConjunctionModule):
                    target_module.register_source(source_name)

    def push_button(
            self,
            sources_to_track: Iterable[str] | None = None,
    ) -> tuple[Counter[bool], set[str]]:
        if sources_to_track is None:
            sources_to_track = set()
        sources_to_track_set = set(sources_to_track)
        tracked_sources: set[str] = set()

        # First pulse is a single low pulse from the button to the
        # broadcaster, which is also sent to the broadcaster's targets
        pulse_counts = Counter([False])
        queue: deque[tuple[str, bool, str]] = deque(
            ("broadcaster", False, t) for t in self.broadcaster_targets
        )
        while queue:
            source, is_high_pulse, target = queue.popleft()
            pulse_counts[is_high_pulse] += 1

            # Track high pulses sent from the given modules
            if source in sources_to_track_set and is_high_pulse:
                tracked_sources.add(source)

            if target not in self.modules:
                continue

            module = self.modules[target]
            outgoing_pulse = module.receive(source, is_high_pulse)
            if outgoing_pulse is not None:
                queue.extend(
                    (module.name, outgoing_pulse, t)
                    for t in module.targets
                )

        return pulse_counts, tracked_sources


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 20.
    """
    _year = 2023
    _day = 20

    @answer(794930686)
    def part_1(self) -> int:
        computer = Computer(self.input)
        totals = sum(
            (computer.push_button()[0] for _ in range(1000)),
            start=Counter[bool](),
        )
        return totals[False] * totals[True]

    @answer(244465191362269)
    def part_2(self) -> int:
        # HACK There is no "rx" module in the testing data; thus, there
        # is no solution for it.
        if self.testing:
            return 0

        computer = Computer(self.input)
        # NOTE Only one module is able to send a low pulse to "rx", a
        # conjunction module which we will call the "ultimate module".
        ultimate_module = next(
            (
                module
                for module in computer.modules.values()
                if "rx" in module.targets
                and isinstance(module, ConjunctionModule)
            ),
            None,
        )
        assert ultimate_module is not None, "could not find ultimate module"
        sources = ultimate_module.sources

        # NOTE The ultimate module only sends such a pulse when all its
        # sources send it a high pulse simultaneously. Its sources will
        # send high pulses at regular periods.
        periods: dict[str, int] = {}
        for i in count(1):
            _, tracked_sources = computer.push_button(sources)
            for source in tracked_sources:
                # If this is the first high pulse to this module, record
                # the current number of button presses as its period
                periods.setdefault(source, i)

            # Return LCM of periods if all sources' periods are recorded
            if len(sources) == len(periods):
                return lcm(*periods.values())
        assert False  # Infinite loop
