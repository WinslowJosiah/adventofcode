---
year: 2025
day: 11
title: "Reactor"
slug: 2025/day/11
pub_date: "2025-12-12"
# concepts: [recursion]
---
## Part 1

What's the first thing you do when you see a large server rack with data flowing
across devices? Plot it out into a [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)),
of course! Or if you're a Python programmer, parse the input into a `dict`
mapping devices to their outputs.

```py title="2025\day11\solution.py"
def create_graph(lines: list[str]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for line in lines:
        device, outputs = line.split(": ")
        graph[device] = outputs.split()
    return graph
```

How many different paths lead from `you` to `out`? I was a bit worried I'd have
to break out my [`pathfinding` module](https://github.com/WinslowJosiah/adventofcode/blob/main/solutions/utils/pathfinding.py)
to find out, but I didn't have to; the input is a [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
(directed acyclic graph), so a simpler path-counting approach is possible.
Recursion was a lifesaver on [Day 10](/solutions/2025/day/10), so let's use the
following recursive algorithm:

- **Base case**: If this device _is_ the ending device, there is exactly 1 path
to it. (After all, doing nothing counts as a path!)
- **Recursive case**: To count the paths from the start to the end, add up the
number of paths from each possible _next_ device to the end.

One gotcha to watch out for is the possibility of there not being a "next
device"; we can use the [`dict.get`](https://docs.python.org/3/library/stdtypes.html#dict.get)
method to get an empty list of "next devices" if that's the case.

```py title="2025\day11\solution.py"
def num_paths(graph: dict[str, list[str]], start: str, end: str) -> int:
    if start == end:
        return 1
    return sum(
        num_paths(graph, next_node, end)
        for next_node in graph.get(start, [])
    )
```

Putting these functions together...

```py title="2025\day11\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        graph = create_graph(self.input)
        return num_paths(graph, "you", "out")
```

...we get an answer extremely quickly, with not a lot of code. That was easy;
are we in for an easy Part 2 this time?

## Part 2

This time, we only consider a path to be valid if it has visited the `dac` and
`fft` nodes at some point. This requires us to make a few changes to our
`num_paths` function to account for that.

1. We'll add a new parameter called `middle`, which has a group of "middle"
devices that should be visited before the end.
2. If we haven't seen every "middle" device by the end, we say that there are 0
valid paths instead of 1.
3. Before we continue counting paths, if we're currently at a "middle" device,
we mark it as seen.

```py title="2025\day11\solution.py" ins={1,7,9,11,13,16-18,24} ins="if seen == middle_set else 0" ins=", new_seen"
from collections.abc import Iterable

def num_paths(
        graph: dict[str, list[str]],
        start: str,
        end: str,
        middle: Iterable[str] | None = None,
) -> int:
    middle_set = set(middle if middle is not None else ())

    def _num_paths(node: str, seen: set[str]) -> int:
        if node == end:
            # Path is only valid if we've seen every "middle" device
            return 1 if seen == middle_set else 0

        new_seen = seen
        if node in middle_set:
            new_seen = seen | {node}
        return sum(
            _num_paths(next_node, new_seen)
            for next_node in graph.get(node, [])
        )

    return _num_paths(start, set())
```

And in our Part 2 solution, we can pass in the `svr` device as our starting
device, and the `dac` and `fft` devices as our "middle" devices.

```py title="2025\day11\solution.py" ins="svr" ins=", middle=["dac", "fft"]"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        graph = create_graph(self.input)
        return num_paths(graph, "svr", "out", middle=["dac", "fft"])
```

We don't get a result very quickly, however; that's because our path-counting
function does a lot of repeated calculations -- calculations we can avoid
with [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache).
(We also need to make our `seen` and `middle_set` sets into `frozenset`s,
because any arguments to a `@cache`-decorated function must be hashable.)

```py title="2025\day11\solution.py" ins={2,12} ins="frozenset" ins="frozenset[str]"
from collections.abc import Iterable
from functools import cache

def num_paths(
        graph: dict[str, list[str]],
        start: str,
        end: str,
        middle: Iterable[str] | None = None,
) -> int:
    middle_set = frozenset(middle if middle is not None else ())

    @cache
    def _num_paths(node: str, seen: frozenset[str]) -> int:
        if node == end:
            # Path is only valid if we've seen every "middle" device
            return 1 if seen == middle_set else 0

        new_seen = seen
        if node in middle_set:
            new_seen = seen | {node}
        return sum(
            _num_paths(next_node, new_seen)
            for next_node in graph.get(node, [])
        )

    return _num_paths(start, frozenset[str]())
```

We end up with a result in the hundreds of trillions. I have absolutely no idea
how the elves are supposed to figure out which of those paths is causing the
communication problem... but at least we narrowed it down from the
_quadrillions_ of paths it would've been otherwise.
