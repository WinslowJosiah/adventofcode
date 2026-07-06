---
year: 2024
day: 16
title: "Reindeer Maze"
slug: 2024/day/16
pub_date: "2026-07-06"
# concepts: [recursion]
---
## Part 1

Another day, another grid puzzle. A _pathfinding_ puzzle, in fact... which
reminds me a bit of [2023 Day 17](/solutions/2023/day/17). That day, we were
also trying to minimize some metric in a path through a grid, where doing
different things had different costs in that metric.

In my solution to 2023 Day 17, I thought of the grid as a weighted graph, where
moving to different nodes incurred different "weights"; that way, I could use
[Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) or
the [A\* algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) to find
the shortest (i.e. lowest-weight) path in the weighted graph. Today, the point
values of the Reindeer moving forward and turning can be thought of the
"weights" in a weighted graph, so I'll be using the same approach here.

To handle these sorts of pathfinding puzzles, I created a custom
[`pathfinding` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/pathfinding.py)
with a function called `find_shortest_paths`. It uses either Dijkstra's
algorithm or A\*, depending on whether you provide a "heuristic" function that
estimates the distance between two states. You can see the code for it below,
and you can read my writeup of [2023 Day 17](/solutions/2023/day/17) for an
explanation of how it works.

:::details
:summary[My `pathfinding` module (so far)]

```py title="utils/pathfinding.py" collapse={1-30,39-46}
# pyright: reportArgumentType=false
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable
from dataclasses import dataclass
from heapq import heapify, heappop, heappush
from math import inf
from typing import Protocol

class PathState[Node](Hashable, Protocol):
    """
    Protocol defining the interface for states used in pathfinding.
    """
    @property
    def node(self) -> Node: ...

# HACK The type checker complains when I constrain the generic typevar
# State by PathState[Node], since Node is also a generic typevar. The
# only thing I can do about this seems to be to ignore it. (This will
# happen repeatedly throughout this module.)
@dataclass(frozen=True)
class PathResult[Node, State: PathState[Node]]:  # pyright: ignore[reportGeneralTypeIssues]
    """
    Result of `find_shortest_paths`.
    """
    distance: int

# Custom exception: no path exists
class NoPathError(Exception):
    """No path exists from the start states to the end node."""
    pass

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    start_states_set: set[State] = set(start_states)
    if not start_states_set:
        raise ValueError("start_states must be non-empty")
    # Verify all start states have the same node
    start_node = next(iter(start_states_set)).node
    if not all(s.node == start_node for s in start_states_set):
        raise ValueError("all start states must have the same node")

    distances: dict[State, int | float] = defaultdict(
        lambda: inf,
        {(s, 0) for s in start_states_set},
    )

    # NOTE For A*, priority = distance + heuristic; for Dijkstra,
    # priority is distance.
    def get_priority(distance: int, node: Node) -> int:
        return distance + (heuristic(node, end_node) if heuristic else 0)

    priority_queue: list[tuple[int, int, State]] = [
        (get_priority(0, s.node), 0, s)
        for s in start_states_set
    ]
    heapify(priority_queue)
    shortest_distance: int | None = None

    while priority_queue:
        _, distance, state = heappop(priority_queue)

        # If we've found an end state, record the distance
        if state.node == end_node:
            shortest_distance = distance
            break

        # Skip if we've already found this state with a lower distance
        if distances[state] < distance:
            continue

        for next_state, distance_to_next_state in get_transitions(state):
            prev_distance = distances[next_state]
            next_distance = distance + distance_to_next_state

            # If this is a lower-distance way to get here
            if next_distance < prev_distance:
                # Update distances and continue searching from here
                distances[next_state] = next_distance
                priority = get_priority(next_distance, next_state.node)
                heappush(priority_queue, (priority, next_distance, next_state))

    if shortest_distance is None:
        raise NoPathError(
            f"no path exists from {start_node!r} to {end_node!r}"
        )

    return PathResult(
        distance=shortest_distance,
    )
```

:::

The hard part is already done, so let's quickly finish up Part 1!

---

To use my `find_shortest_paths` function, we have to tell it a few things:

1. The starting path states. They must have the same "node" -- location in the
grid -- but they can have different attributes such as facing direction.
2. The ending node. Once a path state reaches this node, the path is finished.
3. How to transition from one path state to another, and the associated weights
of those transitions. This will be in the form of a `get_transitions` function,
which takes a path state and yields each possible next state and the weight of
transitioning to it.
4. _Optionally_, you can provide a "heuristic" function that estimates the
distance between two states. If you can find a good choice of heuristic, it
could speed up the search considerably.[^heuristic]

[^heuristic]: To guarantee the shortest path is found, the heuristic you choose
must be **admissible** (i.e. never overestimate the distance), and to guarantee
the search happens in an optimal order, the heuristic must be **consistent**
(i.e. not decrease the total estimated distance if an intermediate node is
reached first).

    The [last time](/solution/2023/day/17) I used `find_shortest_paths`, I said
    I'd check how much a heuristic could improve the runtime of a solution. The
    best admissible and consistent heuristic I could come up with today was this
    one, which assumes a straight unblocked path to the end.

    ```py title="2024\day16\solution.py"
    def heuristic(a: GridPoint, b: GridPoint):
        (ar, ac), (br, bc) = a, b
        return (
            taxicab_distance(a, b) + (1000 if ar != br and ac != bc else 0)
        )
    ```

    However, I was disappointed to find out that this heuristic made my solution
    slightly _slower_ on my machine, by about 8 milliseconds. I assume this is
    because it doesn't actually do a good job of estimating the true distances
    between nodes. Oh well.

First, we'll parse the grid and find the start and end nodes. I have a custom
[`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
to handle this; you can read my writeups for Days [4](/solutions/2024/day/4),
[6](/solutions/2024/day/6), [8](/solutions/2024/day/8), [10](/solutions/2024/day/10),
[12](/solutions/2024/day/12), and [15](/solutions/2024/day/15) to see how it
works.

```py title="2024\day16\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        start_node = next(k for k, v in grid.items() if v == "S")
        end_node = next(k for k, v in grid.items() if v == "E")
        ...
```

Next, we need a good way to represent the Reindeer. They all have a location in
the grid and a facing direction, so the `Position` class from my `grids` module
is a good choice. (In fact, because my `find_shortest_paths` needs our states to
have a `node` property, we'll want to create a _subclass_ of `Position` that has
such a property.)

```py title="2024\day16\solution.py"
class State(Position):
    # NOTE find_shortest_paths needs a state with a node property.
    @property
    def node(self) -> GridPoint:
        return self.point
```

We'll also want to know which states the Reindeer can transition to and their
respective point totals. They can `rotate` in place clockwise or
counter-clockwise for 1,000 points, or if they're not in front of a wall, they
can `step` forward for 1 point.

```py title="2024\day16\solution.py"
from collections.abc import Iterator

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            # Turn 90 degrees clockwise = 1000 points
            yield s.rotate("CW"), 1000
            # Turn 90 degrees counter-clockwise = 1000 points
            yield s.rotate("CCW"), 1000
            # Move forward = 1 point
            if s.next_point in grid:
                yield s.step(), 1
        ...
```

Finally, we can put it all together with a call to `find_shortest_paths`. (The
Reindeer start at the start node facing right; this is our only starting state.)

```py title="2024\day16\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        path_result = find_shortest_paths(
            [State(start_node, Direction.RIGHT)],
            end_node,
            get_transitions=get_transitions,
        )
        return path_result.distance
```

The `distance` property of the result will have the lowest point total the
Reindeer can achieve! Looks like my `pathfinding` module greatly simplified our
code here.

## Part 2

Before, my `pathfinding` module simply returned the _distance_ of the shortest
path. But for this puzzle, I think it's a good idea to rework it to return the
shortest path _itself_ -- or _all_ shortest paths, if more than one exists.[^more-than-one-path]
So let's do that first.

[^more-than-one-path]: The fact that there could be more than one shortest path
is secretly the reason I called it `find_shortest_paths` instead of
`find_shortest_path`.

---

Before we proceed, let's modify my `PathResult` class to not just store the
distance, but the actual paths (as lists of path states).

```py title="utils/pathfinding.py" ins=", Iterator" ins={18}
from collections.abc import Callable, Hashable, Iterable, Iterator
from dataclasses import dataclass
from typing import Protocol

class PathState[Node](Hashable, Protocol):
    """
    Protocol defining the interface for states used in pathfinding.
    """
    @property
    def node(self) -> Node: ...

@dataclass(frozen=True)
class PathResult[Node, State: PathState[Node]]:  # pyright: ignore[reportGeneralTypeIssues]
    """
    Result of `find_shortest_paths`.
    """
    distance: int
    paths: Iterator[list[State]]
```

First, we need to change how we handle finding an end state. Currently, we
`break` out of the main loop as soon as we find a single end state; we'll want
to change this to find _all_ possible end states, as long as they end some
shortest path. The end states we reach will be saved in an `end_states` list for
our convenience.

```py title="utils/pathfinding.py" ins={11,17,19-21,23-24}
...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    ...
    end_states: list[State] = []

    while priority_queue:
        _, distance, state = heappop(priority_queue)
        # If we've found an end state, record the distance
        if state.node == end_node:
            if shortest_distance is None:
                shortest_distance = distance
            # Continue until we exceed the shortest distance (so we find
            # all ending states at the same distance)
            if distance > shortest_distance:
                break
            end_states.append(state)
            continue
        ...
    ...
```

Second, we need to record some more information during the main loop. In order
to reconstruct the shortest paths, we're going to store the _previous_ states
for all states we visit, so we can eventually build each shortest path going
_backwards_ from the end to the start.

We'll do this by creating a `dict` mapping path states to a `set` of all of its
previous path states; first we clear this `set` if our current path to this
state is _more_ optimal than before, and then we add the previous state to this
`set` if our current path is _at least_ as optimal as before.

```py title="utils/pathfinding.py" ins={13,31-32,34-37}
from collections import defaultdict
...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    ...
    end_states: list[State] = []
    prev_states: dict[State, set[State]] = defaultdict(set)

    while priority_queue:
        ...
        # Skip if we've already found this state with a better distance
        if distances[state] < distance:
            continue

        for next_state, distance_to_next_state in get_transitions(state):
            prev_distance = distances[next_state]
            next_distance = distance + distance_to_next_state

            # If this is a lower-distance way to get here
            if next_distance < prev_distance:
                # Update distances and continue searching from here
                distances[next_state] = next_distance
                priority = get_priority(next_distance, next_state.node)
                heappush(priority_queue, (priority, next_distance, next_state))
                # No other path to here has been optimal yet
                prev_states[next_state].clear()

            # If this isn't a higher-distance way to get here
            if next_distance <= prev_distance:
                # The state we got here from is on an optimal path
                prev_states[next_state].add(state)
    ...
```

And finally, we need to use this new information to construct every possible
shortest path. Each shortest path can be walked through _in reverse_ by taking
our previous-states `dict`, starting at an ending state, and moving backwards
until we reach a starting state; we can therefore find _all_ shortest paths by
finding _all_ possible previous-state paths from an ending state to a starting
state.

To do this, I created a small `paths_ending_at` function which takes a path
state and yields all paths ending at that state. This is easy to do using
recursion:

- **Base case**: If the current path state _is_ a starting state, the result is
a path consisting of only that starting state itself.
- **Recursive case**: First, find all paths ending at all _previous_ states;
then, the results will be each of those paths with the current state appended to
them.

To get _all_ paths to _all_ ending states, I simply `map` that function over all
the ending states we've seen, and use [`itertools.chain.from_iterable`](https://docs.python.org/3/library/itertools.html#itertools.chain.from_iterable)
to collect all the paths into a single iterable for easy consumption.

```py title="utils/pathfinding.py" ins={1,17-25,27,31}
from itertools import chain
...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    ...
    if shortest_distance is None:
        raise NoPathError(
            f"no path exists from {start_node!r} to {end_node!r}"
        )

    # Generate all paths lazily
    def paths_ending_at(state: State) -> Iterator[list[State]]:
        """Generate all paths ending at `state`."""
        if state in start_states_set:
            yield [state]
            return
        for prev_state in prev_states[state]:
            for path in paths_ending_at(prev_state):
                yield path + [state]

    all_paths = chain.from_iterable(map(paths_ending_at, end_states))

    return PathResult(
        distance=shortest_distance,
        paths=all_paths,
    )
```

:::tip
Note that, instead of making `paths_ending_at` a regular function that `return`s
the paths, I made it a _generator_ function that `yield`s the paths. This has
two major benefits:

1. The values `yield`ed from the function are not created and stored all at
once, saving the time and space needed to collect all the resulting values.
2. Each resulting value is calculated and `yield`ed _only_ if needed; the user
can choose to stop generating new values at any time, which saves time in cases
where only _some_ results are needed.

:::

And just like that, we now have an efficient way to not just find the _distance_
of the shortest paths in a weighted graph, but the _shortest paths_ themselves!
This will be extremely useful for any pathfinding problem we come across.

---

The fact that we can now obtain every lowest-point path through the grid makes
Part 2 almost trivial; we can collect all nodes from all such paths into a `set`
and return its length using `len`.

```py title="2024\day16\solution.py" ins="solve" ins="tuple[int, int]" ins=", len(all_nodes)" ins={11-15}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        path_result = find_shortest_paths(
            [State(start_node, Direction.RIGHT)],
            end_node,
            get_transitions=get_transitions,
        )
        all_nodes = set(
            state.node
            for path in path_result.paths
            for state in path
        )
        return path_result.distance, len(all_nodes)
```

Don't you just _love_ useful modules like this that do all the hard work for
you? Well, I hope this shows you that even _you_ could create such a module,
piece by piece, for your _own_ tasks! It's a very rewarding and fulfilling
experience.
