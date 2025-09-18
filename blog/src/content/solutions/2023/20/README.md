---
year: 2023
day: 20
title: "Pulse Propagation"
slug: 2023/day/20
pub_date: "2026-11-11"
# concepts: [oop]
---
## Part 1

We've got a bunch of communication modules sending pulses to each other. This
seems like a perfect occasion for [object-oriented programming](https://en.wikipedia.org/wiki/Object-oriented_programming);
each communication module can inherit from a base class for its shared
properties, and each module type can have unique properties and behaviors of its
own.

First, let's think about what the structure of the objects should be. Obviously,
each module should be an object. Let's use the builtin [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
module[^python-module] to make our base class a "dataclass" (so we can avoid
writing a bit of boilerplate code).

[^python-module]: Not to be confused with the communication "modules" in the
puzzle!

```py title="2023\day20\solution.py"
from dataclasses import dataclass

@dataclass
class BaseModule:
    ...
```

But what kinds of properties should a module have? Well, it has a name, which is
a string... that's an easy one.

```py title="2023\day20\solution.py" ins={5}
from dataclasses import dataclass

@dataclass
class BaseModule:
    name: str
    ...
```

As for sending pulses to other modules, a module would have to know (in some
sense) which other modules it's sending them to. You would think this means that
each module should be able to access the _module objects_ it's sending pulses
to, but that would actually be bad practice; the objects would become tightly
coupled, dependent on each other's implementation details, and more difficult to
debug and change.

So instead, we're going to use something similar to the [mediator pattern](https://en.wikipedia.org/wiki/Mediator_pattern).
There will be one object (which we'll call `Computer`) that knows about all of
the modules, and when each module receives a pulse and sends out its own, it
will basically say "`Computer`, please send this pulse to all of these modules
for me".[^mediator-reference] To do that, it would need to at least know the
_names_ of its target modules, which we'll store as a list of strings.

[^mediator-reference]: This is usually done by (in terms of this puzzle) giving
each module object a reference to the `Computer`, and allowing the module to
call a `Computer.send` method when it wants to send a pulse to another module.
But I don't end up doing that, because the pulse-sending and pulse-receiving
only happens when a button-pushing method on `Computer` is being called anyway.

```py title="2023\day20\solution.py" ins={6}
from dataclasses import dataclass

@dataclass
class BaseModule:
    name: str
    targets: list[str]
    ...
```

A module should be able to do one thing: react to a pulse that is sent to it.
How it reacts will depend on which module the pulse is coming from, as well as
the pulse itself. The result may be a high/low pulse, or no pulse at all; the
`Computer` object can take the resulting pulse (if any) and dispatch it to the
target modules. So we'll define a `receive` method that each module type can
implement differently.

```py title="2023\day20\solution.py" ins={1,9-11} ins="(ABC)"
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BaseModule(ABC):
    name: str
    targets: list[str]

    @abstractmethod
    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        ...
```

:::note
I'm using the [`abc`](https://docs.python.org/3/library/abc.html) module to make
this class [abstract](https://en.wikipedia.org/wiki/Class_(programming)#Abstract)
-- because we don't want to simply have a `BaseModule` without it being a
specific _kind_ of module -- and make the `receive` method an "abstract method"
-- because we want `receive` to be implemented in any `BaseModule` subclass.
:::

Now we can implement the different module types.

First, the flip-flop module. It remembers an internal on/off state, which is off
by default and cannot be configured. We can use the `field` method provided by
`dataclasses` to create a field with a default value of `False` and which can't
be provided to the class's `__init__` function.[^field-repr-false]

[^field-repr-false]: I also pass in `repr=False`, so this field doesn't show up
in the string representation. This made it slightly easier for me to debug,
because printing the object shows less unnecessary information.

```py title="2023\day20\solution.py" ins=", field"
from dataclasses import dataclass, field

@dataclass
class FlipFlopModule(BaseModule):
    _state: bool = field(default=False, init=False, repr=False)

    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        if is_high_pulse:
            return None
        self._state = not self._state
        return self._state
```

The `receive` implementation is straightforward. (Remember, we will return
`None` in the case of no pulse being sent!)

Next, the conjunction module. It remembers its source modules and the most
recent pulses they sent, which defaults to a low pulse for each source module;
this also cannot be configured. We can represent these source states as a `dict`
and create a field for them (using `default_factory` instead of `default`,
because a mutable value as a `default` doesn't work).

The only issue is, each conjunction module would need to know which modules have
it as a target, and there's no easy way to initialize it with this information.
But once the `Computer` class finds each conjunction module's sources, we could
just have it call a `register_source` function we define so the module knows
about them.

```py title="2023\day20\solution.py"
@dataclass
class ConjunctionModule(BaseModule):
    _source_states: dict[str, bool] = field(
        default_factory=dict[str, bool],
        init=False,
        repr=False,
    )

    def receive(self, source: str, is_high_pulse: bool) -> bool | None:
        self._source_states[source] = is_high_pulse
        return not all(self._source_states.values())

    def register_source(self, source: str) -> None:
        self._source_states[source] = False
```

`receive` is also straightforward to implement for this class, if you remember
that `all` can be used to check if every item of an iterable is true.

:::tip
Ever since Python 3.9, type annotations such as `dict[str, bool]` are actually
callable! Calling them will return a [generic alias type](https://docs.python.org/3/library/stdtypes.html#types-genericalias),
which will help out type checkers and otherwise act like a regular `dict`. (This
can also be done with [several other builtin types](https://docs.python.org/3/library/stdtypes.html#standard-generic-classes),
such as `tuple`, `list`, and `set`.)

```py
>>> dict_generic = dict()
>>> dict_parameterized = dict[str, bool]()
>>> dict_generic == dict_parameterized
True
```

So if your type checker ever complains about using one of those types as a
callable on its own (which should be rare), you can use the more specific type
instead. That way, you don't have to [break the rules](https://pep20.org/#special)
-- say, with a call to `typing.cast`, or with a `# type: ignore` comment -- to
handle that special case.
:::

Now to implement the `Computer` class, which will be storing and interfacing
with all of these modules. Its `__init__` function will take the puzzle input,
parse it into all the module objects, and store them in a `dict` so it can find
them by name. This is mostly simple, but there are two extra things it does:

- If the name of the module is `broadcaster`, it stores the target names in a
list called `self.broadcaster_targets` (instead of creating a module).[^broadcast-module]
- After the modules are initialized, the conjunction modules don't yet know what
their source modules are. So each module is looped through, and if it targets
any conjunction modules, it's registered as a source of those conjunction
modules.

[^broadcast-module]: I didn't write a `BroadcastModule` class for this because
it's not really necessary; there'd only ever be one instance of it, and it would
simply broadcast to its targets whatever pulse was sent to it by the button
module. In this case, I found it easier to make the `Computer` do this manually
when it needs to. (This is also why I don't have a `ButtonModule` class.)

```py title="2023\day20\solution.py"
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
```

Now to handle pushing the button! We will use a [`deque`](https://docs.python.org/3/library/collections.html#collections.deque)
to store the source module, lowness/highness, and target module of each pulse,
and we will use a [`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter)
to count the low/high pulses. Each pulse will be received by the target module,
and the new pulse that is returned (if any) will be put in the queue to be sent
to all of its targets.

```py title="2023\day20\solution.py"
from collections import Counter, deque

class Computer:
    ...

    def push_button(self) -> Counter[bool]:
        # First pulse is a single low pulse from the button to the
        # broadcaster, which is also sent to the broadcaster's targets
        pulse_counts = Counter([False])
        queue: deque[tuple[str, bool, str]] = deque(
            ("broadcaster", False, t) for t in self.broadcaster_targets
        )
        while queue:
            source, is_high_pulse, target = queue.popleft()
            pulse_counts[is_high_pulse] += 1

            if target not in self.modules:
                continue

            module = self.modules[target]
            outgoing_pulse = module.receive(source, is_high_pulse)
            if outgoing_pulse is not None:
                queue.extend(
                    (module.name, outgoing_pulse, t)
                    for t in module.targets
                )

        return pulse_counts
```

All that remains is to push the button 1,000 times. And because `Counter`s can
be added together, we can simply `sum` the results of calling
`Computer.push_button` 1,000 times. But we need to provide an empty `Counter` as
the starting value, or else we get an error:

```py
>>> from collections import Counter
>>> a, b = Counter("cabbage"), Counter("feed")
>>> sum([a, b])
TypeError: unsupported operand type(s) for +: 'int' and 'Counter'
>>> sum([a, b], start=Counter())
Counter({'e': 3, 'a': 2, 'b': 2, 'c': 1, 'g': 1, 'f': 1, 'd': 1})
```

This is because the `start` argument defaults to 0 -- which makes sense, because
you normally use `sum` to add numbers anyway.[^sum-start-string]

[^sum-start-string]: Fun fact: you can use `sum` to "sum" anything _except_
strings. You get an error if you do; [the docs](https://docs.python.org/3/library/functions.html#sum)
recommend you use `''.join` for strings instead.

```py title="2023\day20\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        computer = Computer(self.input)
        totals = sum(
            (computer.push_button() for _ in range(1000)),
            start=Counter[bool](),
        )
        return totals[False] * totals[True]
```

From here, getting the answer is as easy as multiplying the number of low and
high pulses in the resulting `Counter`. On to Part 2!

## Part 2

How many times must we press the button for a low pulse to be sent to `rx`?
Looking at my puzzle input, I notice that only one module can do this -- a
conjunction module named `lx` (the name will be different for you). I'll call
this module the "ultimate module", and its inputs the "penultimate modules".

Before we proceed, we should probably write something that gives us the names of
the inputs for a conjunction module. Luckily for us, `ConjunctionModule`s know
exactly what their sources are, and they store them in a `dict`, so getting
their sources is just a matter of getting the keys of that `dict`.[^i-wonder-who]

[^i-wonder-who]: I wonder who coded up _that_ little implementation detail...

```py title="2023\day20\solution.py" ins={5-7}
@dataclass
class ConjunctionModule(BaseModule):
    ...

    @property
    def sources(self) -> list[str]:
        return list(self._source_states.keys())
```

Now we can use this property to get the ultimate module and its sources. Let's
print them out for debugging.

```py title="2023\day20\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def _debug_modules(self):
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

        print("ultimate module:", ultimate_module)
        print("sources:")
        for source in sources:
            print(source)
```

Here's the result I get for my input (the names will be different for your
input):

```text
ultimate module: ConjunctionModule(name='lx', targets=['rx'])
sources:
ConjunctionModule(name='cl', targets=['lx'])
ConjunctionModule(name='rp', targets=['lx'])
ConjunctionModule(name='lb', targets=['lx'])
ConjunctionModule(name='nj', targets=['lx'])
```

Because the ultimate module is a single `ConjunctionModule`, it will only send a
low pulse if it remembers a high pulse for all of its source modules (i.e. the
penultimate modules). When does this happen?

After some more debugging, I found out that each of the penultimate modules
seems to get in a cycle; it will send a low pulse most of the time, but it will
send a high pulse at $n$ button presses, another high pulse at $2n$ button
presses, another at $3n$ button presses, etc. So we're looking for when every
penultimate module sends a high pulse simultaneously, and it will be the :abbr[LCM]{title="least common multiple"}
of the lengths of these cycles. This is turning out a lot like [Day 8](/solutions/2023/day/8),
except the cycles were _way_ harder to spot this time.

First, let's modify the `Computer.push_button` function to track high pulses
from arbitrary modules. We can simply pass their names in as an optional
argument, and add them to a `set` that we keep track of while processing pulses.

```py title="2023\day20\solution.py" ins={1,7,9-12,20-22} ins="tuple[" ins=", set[str]]" ins=", tracked_sources"
from collections.abc import Iterable

class Computer:
    ...
    def push_button(
            self,
            sources_to_track: Iterable[str] | None = None,
    ) -> tuple[Counter[bool], set[str]]:
        if sources_to_track is None:
            sources_to_track = set()
        sources_to_track_set = set(sources_to_track)
        tracked_sources: set[str] = set()

        ...

        while queue:
            source, is_high_pulse, target = queue.popleft()
            pulse_counts[is_high_pulse] += 1

            # Track high pulses sent from the given modules
            if source in sources_to_track_set and is_high_pulse:
                tracked_sources.add(source)

            ...

        return pulse_counts, tracked_sources
```

:::caution

By returning both the pulse `Counter` and tracked-high-pulses `set`, we've
broken our Part 1 solution which expects only the `Counter`. But that's nothing
that can't be fixed by indexing the result.

```py title="2023\day20\solution.py" ins="[0]"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        computer = Computer(self.input)
        totals = sum(
            (computer.push_button()[0] for _ in range(1000)),
            start=Counter[bool](),
        )
        return totals[False] * totals[True]
```

This is the kind of thing a type checker would catch and warn you about before
you run your code. This is why I think they're helpful!
:::

Today will end much like Day 8 did: by finding the cycle lengths (which I'm
storing in a `dict` called `periods`) and getting their [`lcm`](https://docs.python.org/3/library/math.html#math.lcm)
once I have them. Notably, I'm using the [`dict.setdefault`](https://docs.python.org/3/library/stdtypes.html#dict.setdefault)
method to store the amount of button presses; it is stored if the entry doesn't
exist, and ignored if it does.

```py title="2023\day20\solution.py" ins={1-2,24-38} ins="part_2"
from itertools import count
from math import lcm
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
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
```

Yet another example of the genre of puzzle which forces you to notice some
non-trivial features of the puzzle input.[^not-in-sample-input] Again, not a
fan.

[^not-in-sample-input]: Which are _not_ in the sample input -- as if I needed to
clarify this time.

:::note[Observations]
Some folks in [the Reddit solution thread](https://reddit.com/comments/18mmfxb)
noticed that the module connections behaved just like four 12-bit binary
counters. That's kind of cool.

As well, it seems that for everyone who's shared details of their puzzle inputs,
all the periods of the cycles are prime numbers. Mine were 3,733, 3,911, 4,091,
and 4,093, so that tracks. That means their :abbr[LCM]{title="least common multiple"}
is just their product, and I didn't need the `math.lcm` method after all. Oh
well.
:::
