from collections import deque
from collections.abc import Iterable, Sequence
from typing import cast


class BaseModule:
    def __init__(
            self,
            name: str,
            destinations: Sequence[str],
            mediator: "Mediator | None" = None,
    ):
        """
        Base class for all modules (communication modules connected to
        the Desert Island sand machines with long cables).

        This class defines some basic properties, a `send_pulse` method,
        and an empty `receive_pulse` method.
        """
        self._name = name
        self._destinations = list(destinations)
        self._mediator = mediator

    @property
    def name(self) -> str:
        return self._name

    @property
    def destinations(self) -> list[str]:
        return self._destinations

    @property
    def mediator(self) -> "Mediator | None":
        return self._mediator

    @mediator.setter
    def mediator(self, mediator: "Mediator"):
        self._mediator = mediator

    def send_pulse(self, pulse_high: bool):
        assert self._mediator is not None
        for dest_name in self._destinations:
            self._mediator.send_pulse(self, dest_name, pulse_high)

    def receive_pulse(self, sender_name: str, pulse_high: bool):
        pass


class FlipFlopModule(BaseModule):
    def __init__(
            self,
            name: str,
            destinations: Sequence[str],
            mediator: "Mediator | None" = None,
    ):
        """
        Create a flip-flop module.

        Flip-flop modules have an internal on/off state, which starts as
        off. If the module receives a high pulse, nothing happens. If
        the module receives a low pulse, it flips its internal state,
        then it sends a pulse (high if the module turned on, low if the
        module turned off).
        """
        super().__init__(name, destinations, mediator)
        self._state = False

    def receive_pulse(self, sender_name: str, pulse_high: bool):
        if not pulse_high:
            self._state = not self._state
            self.send_pulse(self._state)


class ConjunctionModule(BaseModule):
    def __init__(
            self,
            name: str,
            destinations: Sequence[str],
            mediator: "Mediator | None" = None,
    ):
        """
        Create a conjunction module.

        Conjunction modules keep track of the latest pulse received from
        each module that connects to it. When the module receives a
        pulse, it updates its memory for that input, then it sends a
        pulse (low if it now remembers high pulses for all its inputs,
        high if it doesn't).
        """
        super().__init__(name, destinations, mediator)
        self._inputs: dict[str, bool] = {}
        # NOTE: This property must be kept track of for Part 2.
        self._first_high_pulse: int | None = None

    def add_input(self, input_name: str):
        self._inputs[input_name] = False

    @property
    def first_high_pulse(self) -> int | None:
        return self._first_high_pulse

    def send_pulse(self, pulse_high: bool):
        assert self.mediator is not None
        # If this module is sending a high pulse for the first time
        if pulse_high and self._first_high_pulse is None:
            # Save the index of this high pulse
            self._first_high_pulse = self.mediator.button_pushes

        return super().send_pulse(pulse_high)

    def receive_pulse(self, sender_name: str, pulse_high: bool):
        self._inputs[sender_name] = pulse_high
        self.send_pulse(not all(self._inputs.values()))


class BroadcastModule(BaseModule):
    def __init__(self,
            name: str,
            destinations: Sequence[str],
            mediator: "Mediator | None" = None,
    ):
        """
        Create a broadcast module.

        When the module receives a pulse, it sends the same pulse.
        """
        super().__init__(name, destinations, mediator)

    def receive_pulse(self, sender_name: str, pulse_high: bool):
        self.send_pulse(pulse_high)


class Mediator:
    def __init__(self, *modules: BaseModule):
        """
        Create a mediator among a collection of modules.

        The mediator performs actions on behalf of the modules; for
        example, a module that wishes to send a pulse to another module
        must notify the mediator, and then the mediator sends the pulse.
        """
        # Mapping between module names and module instances
        self._modules: dict[str, BaseModule] = {}
        # The broadcaster module, if found
        broadcaster: BroadcastModule | None = None
        # Mapping between module names and instances for conjunction
        # modules
        conjunctions: dict[str, ConjunctionModule] = {}
        # NOTE: We track the conjunction modules because they need to
        # know which modules provide input to them.

        # Process each module
        for module in modules:
            # This mediator is the module's mediator
            module.mediator = self
            self._modules[module.name] = module

            if isinstance(module, BroadcastModule):
                broadcaster = module
            elif isinstance(module, ConjunctionModule):
                conjunctions[module.name] = module

        # NOTE: We are assuming that there is exactly one broadcaster.
        assert broadcaster is not None
        self._broadcaster = broadcaster

        # Gather inputs of each conjunction module
        for name, module in self._modules.items():
            for dest_name in module.destinations:
                destination = conjunctions.get(dest_name, None)
                if destination is not None:
                    destination.add_input(name)

        self._pulses: deque[tuple[str, str, bool]] = deque()
        self._high_pulses = 0
        self._low_pulses = 0
        self._button_pushes = 0

    @property
    def high_pulses(self) -> int:
        return self._high_pulses

    @property
    def low_pulses(self) -> int:
        return self._low_pulses

    @property
    def button_pushes(self) -> int:
        return self._button_pushes

    def push_button(self):
        self._button_pushes += 1
        self.send_pulse(None, self._broadcaster.name, False)

        # Pulses are sent in the order that they are requested
        while self._pulses:
            sender_name, dest_name, pulse_high = self._pulses.popleft()
            self._modules[dest_name].receive_pulse(
                sender_name, pulse_high
            )

    def send_pulse(
            self,
            sender: BaseModule | None,
            dest_name: str,
            pulse_high: bool,
    ):
        if pulse_high:
            self._high_pulses += 1
        else:
            self._low_pulses += 1

        destination = self._modules.get(dest_name, None)
        if destination is None:
            return
        sender_name = "" if sender is None else sender.name
        self._pulses.append((sender_name, dest_name, pulse_high))

    def get_module(self, name: str) -> BaseModule:
        module = self._modules.get(name, None)
        if module is None:
            raise ValueError(f"module {name} doesn't exist")
        return module

    def get_input_modules(self, dest_name: str) -> list[BaseModule]:
        return [
            module
            for module in self._modules.values()
            if dest_name in module.destinations
        ]


def parse_modules(lines: Iterable[str]) -> Mediator:
    """
    Parse a list of lines into a collection of modules.
    """
    modules: list[BaseModule] = []

    for line in lines:
        name, destinations_str = line.split(" -> ")
        destinations = destinations_str.split(", ")

        if name == "broadcaster":
            module = BroadcastModule(name, destinations)
        else:
            module_type, name = name[0], name[1:]
            match module_type:
                case "%":
                    module = FlipFlopModule(name, destinations)
                case "&":
                    module = ConjunctionModule(name, destinations)
                case _:
                    raise ValueError(f"Invalid module type: {module_type}")

        modules.append(module)

    return Mediator(*modules)


def aoc2023_day20_part1(lines: Iterable[str]) -> int:
    mediator = parse_modules(lines)
    # Push the button 1,000 times
    for _ in range(1000):
        mediator.push_button()
    # Multiply the number of low and high pulses sent
    return mediator.low_pulses * mediator.high_pulses


def aoc2023_day20_part2(lines: Iterable[str]) -> int:
    from math import lcm

    mediator = parse_modules(lines)
    # NOTE: We are being asked to figure out when a single low pulse is
    # sent to "rx". Certain things are true about the input data that
    # make this easier to figure out without brute force:
    # 1. The only input to "rx" is a single conjunction module (in my
    # case, "lx").
    # 2. The only input to each input to "lx" is also a single
    # conjunction module.
    # 3. Each input to "lx" only sends a high pulse periodically (and
    # sends a low pulse at all other times).
    # This means that the correct number of button presses is the LCM
    # (lowest common multiple) of the period lengths for each input to
    # "lx".

    input_modules = mediator.get_input_modules("rx")
    # If there isn't exactly one input to "rx", don't run this code
    if len(input_modules) != 1:
        return -1

    # Get input to "rx"
    input_module = cast(ConjunctionModule, next(iter(input_modules)))
    # Get inputs to input to "rx"
    pre_input_modules = cast(
        list[ConjunctionModule],
        mediator.get_input_modules(input_module.name),
    )

    # Push the button until every relevant module outputs a high pulse
    while any(
        module.first_high_pulse is None
        for module in pre_input_modules
    ):
        mediator.push_button()
    # Get the LCM of the period lengths
    first_high_pulses = cast(
        list[int],
        [module.first_high_pulse for module in pre_input_modules],
    )
    return lcm(*first_high_pulses)


parts = (aoc2023_day20_part1, aoc2023_day20_part2)
