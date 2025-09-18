---
year: 2023
day: 17
title: "Clumsy Crucible"
slug: 2023/day/17
pub_date: "2025-11-03"
# concepts: [astar, dijkstra]
---
## Part 1

Another day, another grid puzzle. This time we're pathfinding, so something like
[Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
should come to mind. Dijkstra's algorithm is a way to find the shortest path
from one node to another in a weighted graph. We can think of the heat loss at
each city block as the "weight" of an edge going to that block, so it seems like
a good approach to go with.

Let's take a short while to implement this algorithm. (I'll be putting it in my
[`pathfinding` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/pathfinding.py)
to use for past and future puzzles, so I'll want this to be as generalized as
possible.) First, the states we traverse through should have a `node` property
(optionally with other information), and the result we get should have a
`distance` property for the shortest distance (along with other information we
can implement later).

```py title="utils\pathfinding.py"
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Protocol

class PathState[Node](Hashable, Protocol):
    """
    Protocol defining the interface for states used in pathfinding.
    """
    @property
    def node(self) -> Node: ...

@dataclass(frozen=True)
class PathResult:
    """
    Result of `find_shortest_paths`.
    """
    distance: int
    ...
```

We can think of Dijkstra's algorithm as a generalization of
[breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
(:abbr[BFS]{title="breadth-first search"}). Recall that in :abbr[BFS]{title="breadth-first search"},
we keep track of a queue of nodes from which to explore the rest of the graph;
the node we explore in each iteration is the node with the shortest distance
from the start.

Dijkstra's algorithm follows the same general process as :abbr[BFS]{title="breadth-first search"},
except it doesn't rely on the queue being ordered from shortest to longest
distance; instead, it uses a data structure called a "[min-priority queue](https://en.wikipedia.org/wiki/Priority_queue)",
which allows its smallest item to be extracted efficiently. Python's built-in
[`heapq`](https://docs.python.org/3/library/heapq.html) module is perfect for
this, as it gives us what we need to make a min-priority queue![^heapq]

[^heapq]: It's called `heapq` because it uses a data structure called a
"min-heap" -- rather, a `list` that is _treated_ as a min-heap. The Python docs
have a section on [how min-heaps work](https://docs.python.org/3/library/heapq.html#theory)
if you're curious.

Our pathfinding function will take in one or more `start_states` (which must
share the same starting node, but can otherwise have different properties), an
`end_node` to calculate the distance to, and a `get_transitions` function for
getting neighboring states and the distances to them.

```py title="utils\pathfinding.py" ins=/(Callable, )Hashable(, Iterable)/
from collections.abc import Callable, Hashable, Iterable

...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
) -> PathResult[Node, State]:
    """
    Find the shortest paths between starting states and an ending node.
    """
    start_states_set: set[State] = set(start_states)
    if not start_states_set:
        raise ValueError("start_states must be non-empty")

    # Verify all start states have the same node
    start_node = next(iter(start_states_set)).node
    if not all(s.node == start_node for s in start_states_set):
        raise ValueError("all start states must have the same node")

    ...
```

First, we assign a distance of 0 to all starting states, and a distance of
infinity to all other states. We can do this with a `defaultdict` where items
have a default value of [`math.inf`](https://docs.python.org/3/library/math.html#math.inf).
Because the `defaultdict` constructor takes a _callable_, not a value, we have
to provide a function that returns infinity, which we can do succinctly with the
[`lambda`](https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions)
keyword, like so:

```py
>>> from collections import defaultdict
>>> from math import inf
>>> distances = defaultdict(lambda: inf, {(0, 0): 0})
>>> distances[0, 0]
0
>>> distances[9, 9]
inf
```

:::note
A `dict` can be created by passing a mapping (or a group of key-value pairs) to
the `dict` function. `defaultdict` will behave similarly; if a mapping (or a
group of key-value pairs) is passed _after_ the first argument to `defaultdict`,
it will be used to populate the `defaultdict`.
:::

The priority queue will simply be a `list` of `tuples` with each distance and
state; we'll use `heapq.heapify` to order it in the way that the `heapq` module
expects.

```py title="utils\pathfinding.py" ins={1-3}
from collections import defaultdict
from heapq import heapify
from math import inf

...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
) -> PathResult[Node, State]:
    ...
    # HACK This type hint isn't strictly correct, because the only
    # possible float value here is infinity.
    distances: dict[State, int | float] = defaultdict(
        lambda: inf,
        {s: 0 for s in start_states_set},
    )
    priority_queue: list[tuple[int, State]] = [
        (0, s)
        for s in start_states_set
    ]
    heapify(priority_queue)
    shortest_distance: int | None = None
    ...
```

For the main loop of the algorithm, we simply loop through the items in the
priority queue, using `heapq.heappop` to take the shortest-distance item from
the queue, and `heapq.heappush` to push an item onto the queue if we've found a
shorter-distance way to get there. This continues until either an ending state
is found or all queue items have been exhausted; we then return the distance to
the ending state.

```py title="utils\pathfinding.py" ins=", heappop, heappush"
from heapq import heapify, heappop, heappush

...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
) -> PathResult[Node, State]:
    ...
    while priority_queue:
        distance, state = heappop(priority_queue)
        # If we've found an end state, record the distance
        if state.node == end_node:
            shortest_distance = distance
            break

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
                heappush(priority_queue, (next_distance, next_state))

    if shortest_distance is None:
        raise ValueError("no path exists")

    return PathResult(distance=shortest_distance)
```

This was a bit of a long tangent, but now we have a function for finding the
shortest path in a weighted graph! We can add some more helpful features later,
but we don't need them yet; this much is enough to solve the puzzle.

---

Our states need to keep track of our position and the number of steps since we
last turned, so I'll use the `Position` class I defined on [Day 16](/solutions/2023/day/16).
I'll also use the [`@property`](https://docs.python.org/3/library/functions.html#property)
decorator to add a `node` property to our states, so we can use them in our
`find_shortest_paths` function.

```py title="2023\day17\solution.py"
from typing import NamedTuple

class State(NamedTuple):
    pos: Position
    steps: int

    # NOTE find_shortest_paths needs a state with a node property.
    @property
    def node(self) -> GridPoint:
        return self.pos.point
```

The starting node is at the top left corner of the grid, and the ending node is
at the bottom right corner. Our `find_shortest_paths` function will also need to
know which states it can travel to and their respective "distances" (i.e. heat
loss), which we will define a function for. We can use the step counter we keep
track of to keep us from moving forward if we've taken more than 3 steps since
last turning.

```py title="2023\day17\solution.py"
from collections.abc import Iterator

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, int)
        start_node = 0, 0
        end_node = len(self.input) - 1, len(self.input[-1]) - 1

        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            if s.node != start_node:
                # Turn left (and reset number of steps)
                next_pos = s.pos.rotate("CCW").step()
                next_state = State(next_pos, steps=1)
                if next_pos.point in grid:
                    yield next_state, grid[next_pos.point]

                # Turn right (and reset number of steps)
                next_pos = s.pos.rotate("CW").step()
                next_state = State(next_pos, steps=1)
                if next_pos.point in grid:
                    yield next_state, grid[next_pos.point]

            if s.steps < 3:
                # Move forward (and increase number of steps)
                next_pos = s.pos.step()
                next_state = State(next_pos, steps=s.steps + 1)
                if next_pos.point in grid:
                    yield next_state, grid[next_pos.point]
        ...
```

Finally, we can pass this information to `find_shortest_paths` and get the
"distance" (i.e. heat loss) of the resulting path! (Our path could start moving
down or right, so we should provide starting states with both directions.)

```py title="2023\day17\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        path_result = find_shortest_paths(
            start_states=[
                State(Position(start_node, Direction.RIGHT), steps=0),
                State(Position(start_node, Direction.DOWN), steps=0),
            ],
            end_node=end_node,
            get_transitions=get_transitions,
        )
        return path_result.distance
```

## Part 2

Now we have to enforce a minimum number of steps before turning; otherwise, this
will be just like Part 1. Let's factor out our Part 1 solution into a function,
and make the necessary changes.

```py title="2023\day17\solution.py" ins={5,7-12,36-37,39-40} ins=" and s.steps >= min_steps" ins="is_valid_state(next_state)" ins=/< (max_steps)/ del={4}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def _solve(self, min_steps: int, max_steps: int) -> int:
        ...
        def is_valid_state(s: State) -> bool:
            # - Position must be in grid
            # - End cannot be reached before minimum steps are taken
            return s.pos.point in grid and (
                s.steps >= min_steps or s.node != end_node
            )

        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            if s.node != start_node and s.steps >= min_steps:
                # Turn left (and reset number of steps)
                next_pos = s.pos.rotate("CCW").step()
                next_state = State(next_pos, steps=1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]

                # Turn right (and reset number of steps)
                next_pos = s.pos.rotate("CW").step()
                next_state = State(next_pos, steps=1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]

            if s.steps < max_steps:
                # Move forward (and increase number of steps)
                next_pos = s.pos.step()
                next_state = State(next_pos, steps=s.steps + 1)
                if is_valid_state(next_state):
                    yield next_state, grid[next_pos.point]
        ...

    def part_1(self) -> int:
        return self._solve(0, 3)

    def part_2(self) -> int:
        return self._solve(4, 10)
```

Now we must ensure that we can only turn after the minimum amount of forward
steps are taken. I also added an `is_valid_state` function, which takes care of
ensuring we stay in the grid, and that we take the minimum amount of forward
steps before reaching the end.

Both parts run in ~5.08 seconds on my machine -- not that bad, but still the
longest-running solution for any puzzle so far this year. Can we do any better?

### Bonus

The [A* algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) is another
shortest-path algorithm, which can outperform Dijkstra's algorithm in many
cases. The way it works is actually very similar to Dijkstra's algorithm, a fact
which I find beautifully illustrated by a YouTube video from Polylog called
["The hidden beauty of the A* algorithm"](https://youtu.be/A60q6dcoCjw).

In short, the A* algorithm depends on a "heuristic function" which estimates the
distance to the ending node, and it adds that to the total distance so far to
get the priority of each item on the priority queue. The priority of an item
will then be an estimate of the total distance from the starting node to the
ending node. (Dijkstra's algorithm can be viewed as the special case where this
heuristic is always 0.)

Modifying the `find_shortest_paths` function to use an optional heuristic
doesn't require a lot of changes; all we need to do is calculate the priority of
an item whenever we add it to the priority queue.

```py title="utils/pathfinding.py" ins={9,15-18,38} ins="get_priority(0, s.node), " ins="_, " ins="priority, "
# pyright: reportArgumentType=false
...

def find_shortest_paths[Node, State: PathState[Node]](  # pyright: ignore[reportGeneralTypeIssues]
        start_states: Iterable[State],  # must be non-empty
        end_node: Node,
        *,
        get_transitions: Callable[[State], Iterable[tuple[State, int]]],
        heuristic: Callable[[Node, Node], int] | None = None,
) -> PathResult[Node, State]:
    """
    Find the shortest paths between starting states and an ending node.
    """
    ...
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
        ...

        for next_state, distance_to_next_state in get_transitions(state):
            prev_distance = distances[next_state]
            next_distance = distance + distance_to_next_state
            # If this is a lower-distance way to get here
            if next_distance < prev_distance:
                # Update distances and continue searching from here
                distances[next_state] = next_distance
                priority = get_priority(next_distance, next_state.node)
                heappush(priority_queue, (priority, next_distance, next_state))
    ...
```

One difficulty of using A* is choosing a heuristic function; to guarantee that
the shortest path is found, it must be **admissible** (i.e. never overestimate
the distance), and to guarantee that nodes are explored optimally, it must be
**consistent** (i.e. not decrease the total estimated distance if an
intermediate node is reached first).[^consistent-heuristic]

[^consistent-heuristic]: Note that a heuristic doesn't have to be consistent to
ensure the shortest path is found. If an inconsistent heuristic is used,
however, A* may explore more nodes than necessary to find it.

A good heuristic for this puzzle would be the `taxicab_distance` function I
showcased on [Day 11](/solutions/2023/day/11) (which I've also exported from my
`pathfinding` module for the sake of convenience). In this situation, taxicab
distance is:

- **Admissible**: The heat loss from one block to another will be at least 1 per
city block travelled.
- **Consistent**: The taxicab distance is, by definition, the shortest distance
between two blocks.

```py title="2023\day17\solution.py" ins={13}
...

class Solution(StrSplitSolution):
    def _solve(self, min_steps: int, max_steps: int) -> int:
        ...
        path_result = find_shortest_paths(
            start_states=[
                State(Position(start_node, Direction.RIGHT), steps=0),
                State(Position(start_node, Direction.DOWN), steps=0),
            ],
            end_node=end_node,
            get_transitions=get_transitions,
            heuristic=taxicab_distance,
        )
        return path_result.distance
```

Using this heuristic reduces the time on my machine from ~5.08 seconds to ~4.65
seconds -- a speedup of ~8.5%. Not amazing, but it _is_ a speedup, and the code
changes were [easy to explain](https://pep20.org/#easy) and implement. I'm
pretty sure the speedup would be greater in a different scenario; next time I
use my `find_shortest_paths` function, I'll remind myself to test that.
