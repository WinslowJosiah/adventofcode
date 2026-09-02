---
year: 2024
day: 18
title: "RAM Run"
slug: 2024/day/18
pub_date: "2026-09-02"
# concepts: []
---
## Part 1

Another day, another grid puzzle. In fact, it's another _pathfinding_ puzzle --
like the one from two days prior. Check out my solution and writeup for
[2023 Day 17](solutions/2023/day/17), as well as [Day 16](/solutions/2024/day/16)
from _this_ year, for a refresher on the pathfinding algorithm I'll be using.

Before we deal with pathfinding, though, we'll deal with input parsing. The
input is in the form of comma-separated grid locations, one for each line; to
convert them to X/Y pairs, we can just `split` each line by commas and convert
them to `tuple`s of `int`s. We'll also put the first 1,024 X/Y pairs in a `set`
of "corrupted" locations for later.[^self-testing]

[^self-testing]: For this puzzle, the size of the grid and the number of
initially corrupted grid locations is different between the testing data and the
full puzzle input. The way I handle this in my Advent of Code solution framework
is to add a `self.testing` attribute, which is true if we're working with the
testing data, and false otherwise.

```py title="2024\day18\solution.py"
from typing import cast

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        GRID_SIZE, NUM_INITIAL_BYTES = (7, 12) if self.testing else (71, 1024)

        coords = [
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        ]
        # Simulate corrupting the initial bytes
        corrupted = set(coords[:NUM_INITIAL_BYTES])
        ...
```

:::note
My [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
has a lot of helper classes and helper functions for dealing with grid-based
Advent of Code puzzles. For example, I define `GridPoint` as simply an alias for
`tuple[int, int]` -- a row/column pair or an X/Y pair, depending on the puzzle.

And in order to tell Python that these `tuple`s we're creating aren't just _any_
old `tuple`s, but `GridPoint`s, I use the [`typing.cast`](https://docs.python.org/3/library/typing.html#typing.cast)
function. It does nothing to the value itself, but it makes my static type
checker _very_ happy.
:::

My implementation of [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
from my [`pathfinding` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/pathfinding.py)
will be doing most of the heavy lifting today. It's a bit overpowered for this
puzzle -- all we strictly _need_ is a good [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
-- but hey, what's the point of special custom modules if you don't _use_ them?

To use my `pathfinding` module, we'll basically want to consider our RAM-running
situation as an interconnected series of "states", each with a location called a
"node" and potentially some other information. In this case, however, the "node"
is the only information we need in our states.

```py title="2024\day18\solution.py" ins=", NamedTuple"
from typing import cast, NamedTuple

# NOTE find_shortest_paths needs a state with a node property.
class State(NamedTuple):
    node: GridPoint
```

Then we'll want to use the module's `find_shortest_paths` function, and provide
it with these three pieces of information:[^heuristic]

[^heuristic]: You can also optionally provide it with a "heuristic" function,
which takes two states and estimates the distance between them. A well-chosen
heuristic can sometimes speed up the pathfinding algorithm, but I didn't find
that to be worth it this time. Maybe _one_ day...

1. A list of starting states -- all with the same node, but perhaps with
different _other_ information if that applies.
    - In this case, we only have one starting state, at node `(0, 0)`.
2. An ending node.
    - Our ending node this time is the bottom-right corner of the grid.
3. A "transition" function, which takes a state and returns all the possible
_next_ states and the distances to them.
    - I usually write these in the form of a [generator](https://docs.python.org/3/howto/functional.html#generators)
    function that `yield`s states and their associated distances. Here, I use
    the `neighbors` function from my `grids` module to get all 4 neighbors of
    this state's node, and `yield` each of them (each with a distance of 1) only
    if those locations in the grid haven't been "corrupted".

The result will be a special dataclass I call a `PathResult`; we'll want its
`distance` property to get the distance of the shortest path from start to
finish.

```py title="2024\day18\solution.py" ins={1}
from collections.abc import Iterator
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        # Prepare the arguments to find_shortest_paths
        start_states = [State((0, 0))]
        end_node = (GRID_SIZE - 1, GRID_SIZE - 1)
        def get_transitions(s: State) -> Iterator[tuple[State, int]]:
            for n in neighbors(s.node, num_directions=4, grid_size=GRID_SIZE):
                if n not in corrupted:
                    yield State(n), 1

        path_result = find_shortest_paths(
            start_states=start_states,
            end_node=end_node,
            get_transitions=get_transitions,
        )
        return path_result.distance
```

That's essentially how my `pathfinding` module works! It took a lot of work to
make it as capable and easy to use as that, but I'd say it was worth it.

## Part 2

The corruption of grid locations won't stop after the first 1,024; it'll just
keep happening, until eventually there won't be a path to the end! So we'll need
to simulate more corruption, and figure out when we will be entirely blocked.

To do this, we need some way to keep track of how far we are along the list of
coordinates we're corrupting -- so that every time we want to corrupt a grid
location, we can just add the _next_ grid location to our `corrupted` set, and
then advance our position in the coordinates sequence. You might think we'd need
to keep track of an explicit index into `coords` for this, but there's a more
Pythonic way: using an [iterator](https://docs.python.org/3/howto/functional.html#iterators).

At their most basic level, iterators are streams of data that you can pull from
one item at a time. Simple iterators can be created from iterable values (e.g.
`list`s, `dict`s, and `set`s) using the [`iter`](https://docs.python.org/3/library/functions.html#iter)
function, and getting the _next_ item from an iterator can be done using the
[`next`](https://docs.python.org/3/library/functions.html#next) function --
unless there are no more items, in which case `StopIteration` is raised.

```py
>>> lst = [1, 2, 3]
>>> it = iter(lst)
>>> next(it)
1
>>> next(it)
2
>>> next(it)
3
>>> next(it)
Traceback (most recent call last):
  File "<python-input-5>", line 1, in <module>
    next(it)
    ~~~~^^^^
StopIteration
```

:::note
In Python, whenever you iterate through something with a `for` loop, it is
internally converted to an iterator, and `next` is continually called on it to
retrieve its next item until it raises `StopIteration` (to signal that there are
no items left). For more about how Python handles iterators and iteration in
general, check out the [Python Design Patterns](https://python-patterns.guide/gang-of-four/iterator/)
webpage on "The Iterator Pattern".
:::

This is the behavior we want our `coords` list to have, so let's instead make it
an iterator by passing its contents to the `iter` function. And to populate the
`corrupted` set with the first 1,024 coordinates, we have to switch over from
using the sequence-slicing syntax to using [`itertools.islice`](https://docs.python.org/3/library/itertools.html#itertools.islice)
-- the standard way to "slice" iterators.

```py title="2024\day18\solution.py" ins="solve" ins="tuple[int, str]" ins="iter(" ins=/    (\\))/ del={11} ins={12}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, str]:
        ...
        coords = iter(
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        )
        # Simulate corrupting the initial bytes
        corrupted = set(coords[:NUM_INITIAL_BYTES])
        corrupted = set(islice(coords, NUM_INITIAL_BYTES))
        ...
```

Let's also take the time to change our shortest-path search from a one-time run
to a loop. We'll want this loop to run until our shortest-path search returns no
results -- which my `pathfinding` module signals by raising a custom exception
called `NoPathError`.

As well, let's prepare our result variables, which I'll call `min_steps` and
`first_blocker`.

- If this is our first time running the search, we'll save the shortest path
distance to `min_steps`.
- Before the end of each iteration of our loop, we'll take the `next` coordinate
from `coords`, add it to our `corrupted` set from before, and save that new
coordinate to `first_blocker` (so that when the loop ends, that will be the
first coordinate that blocked all our possible paths).

```py title="2024\day18\solution.py" ins={6-10,16-26}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, str]:
        ...
        min_steps, first_blocker = None, None
        while True:
            # Find the shortest path through the grid at this point;
            # exit infinite loop if no path exists
            try:
                path_result = find_shortest_paths(
                    start_states=start_states,
                    end_node=end_node,
                    get_transitions=get_transitions,
                )
            except NoPathError:
                break

            # Save the length of the shortest path if not saved before
            if min_steps is None:
                min_steps = path_result.distance

            # Corrupt the next byte (which may be our first blocker)
            coord = next(coords)
            corrupted.add(coord)
            first_blocker = coord
        ...
```

Once this loop ends, we can return our two answers: `min_steps`, and
`first_blocker` as a comma-separated string of coordinates.

```py title="2024\day18\solution.py" ins={6-7}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, str]:
        ...
        assert min_steps is not None and first_blocker is not None
        return min_steps, ",".join(map(str, first_blocker))
```

And with that, we have working code that gives us a solution! The only drawback
is, it takes a pretty long time to run -- over _16 seconds_ on my machine, which
isn't great. Can we do _better_?

---

Clearly, almost all of our time is spent running `find_shortest_paths`, which we
do for _every_ new coordinate in our grid that becomes corrupted. Now, we don't
necessarily have to run it that often; instead, we can choose to keep corrupting
more grid locations until our path to the end is actually blocked! But _how_?

Instead of grabbing `next(coords)` manually, we can run a `for` loop on
`coords`; this steps through the `coords` iterator and keeps grabbing its next
coordinate like we need. And once one of these new corrupted coordinates is in
one of our shortest paths, we can store it to `first_blocker` as before, and
`break` out of the `for` loop.

```py title="2024\day18\solution.py" del={8-11} ins={12-24}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, str]:
        ...
        while True:
            ...
            # Corrupt the next byte (which may be our first blocker)
            coord = next(coords)
            corrupted.add(coord)
            first_blocker = coord
            # Choose an arbitrary path
            path = next(path_result.paths)
            path_nodes = set(state.node for state in path)
            # Corrupt more bytes until this path is blocked
            # NOTE This is faster than corrupting only one byte at a
            # time, because we don't run find_shortest_paths() as often.
            for coord in coords:
                corrupted.add(coord)
                if coord in path_nodes:
                    first_blocker = coord
                    break
            else:
                raise RuntimeError("no blocking byte found")
```

And with that, we have working code that gives us a solution _much_ quicker this
time -- about _400 milliseconds_ on my machine, a massive improvement!
