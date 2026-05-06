---
year: 2024
day: 6
title: "Guard Gallivant"
slug: 2024/day/6
pub_date: "2026-05-06"
# concepts: []
---
## Part 1

Another day, another grid puzzle. And another job for my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py),
which I also used on [Day 4](/solutions/2024/day/4).

Today, we'll be tracking the position of an easily predictable guard through a
grid with various obstacles. The guard will have a location in the grid and a
direction in which she[^guard-pronoun] faces. Luckily, my `grids` module already
has two classes that naturally help us model her behavior: `Direction` and
`Position`.

[^guard-pronoun]: Yes, the guard is a "she". The original prompt refers to the
guard with pronouns such as "she" and "her".

`Direction` allows us to represent the directions up, down, left, and right.
Each direction has an `offset` property (the row/column offset you need to add
to move in that direction), and a `rotate` method that rotates a direction
**C**ounter-**C**lock**W**ise or **C**lock**W**ise.

```py title="utils\grids.py"
from enum import IntEnum

type Rotation = Literal["CCW", "CW"]

class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def rotate(self, towards: Rotation) -> "Direction":
        offset = 1 if towards == "CW" else -1
        return Direction((self.value + offset) % 4)

    @property
    def offset(self) -> GridPoint:
        return _ROW_COLUMN_OFFSETS[self]

_ROW_COLUMN_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}
```

And `Position` is essentially a grid location with a facing direction -- with a
few convenience methods for stepping forward and rotating. This will be our
representation of the gallivanting guard.

```py title="utils\grids.py"
class Position(NamedTuple):
    point: GridPoint
    facing: Direction

    @property
    def next_point(self) -> GridPoint:
        return add_points(self.point, self.facing.offset)

    def step(self) -> Self:
        return type(self)(self.next_point, self.facing)

    def rotate(self, towards: Rotation) -> Self:
        return type(self)(self.point, self.facing.rotate(towards))
```

If you want to see another example of the `Position` class in action, I'd
encourage you to check out my solution to [2023 Day 16](/solutions/2023/day/16),
where I used it to model beams of light. Otherwise, if the use of these classes
seems clear so far, read on!

---

To create our guard, we'll need two pieces of information: her starting point,
and her facing direction. She starts at the location of the `^` character --
which we can find using a generator inside of `next()` -- and facing up.

```py title="2024\day06\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        guard = Position(
            point=next(k for k, v in grid.items() if v == "^"),
            facing=Direction.UP,
        )
        ...
```

We'll want to track the guard, making sure she follows her strict protocol until
she exits the grid. This seems like a good thing to put into a function.

Because we want to count only the unique points the guard has seen, we'll track
those points in a `set` that we return once we're done. After we track the
guard's current point, she will follow her protocol: turn clockwise if about to
walk into an obstacle, otherwise step forward.

```py title="2024\day06\solution.py"
def track_guard(grid: Grid[str], guard: Position) -> set[GridPoint]:
    seen: set[GridPoint] = set()

    while guard.point in grid:
        seen.add(guard.point)

        if grid.get(guard.next_point) == "#":
            guard = guard.rotate("CW")
        else:
            guard = guard.step()

    return seen
```

We also return the set of seen points, so we can count them with `len` to get
our answer.

```py title="2024\day06\solution.py"
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        points_seen = track_guard(grid, guard)
        return len(points_seen)
```

Of course, this assumes that the guard will always eventually exit the grid; if
she _didn't_, and her path went into some sort of loop contained within the
grid, the `track_guard` function would never finish. Though an infinite loop
doesn't happen in our case (because Eric Wastl is nice), this possibility is
something to keep in mind.

## Part 2

As it turns out, we _want_ the guard to get into an infinite loop -- and we'll
accomplish this by placing some obstacle somewhere in the grid. But before we do
that, we'll have to ensure that our `track_guard` function can handle this
scenario.

Two changes will need to be made to `track_guard`:

1. If the guard eventually exits the grid, we'll still return the set of seen
locations. But if the guard gets stuck in an infinite loop, we'll want to return
a different value that we can create a special check for. The [obvious](https://pep20.org/#obvious)
choice here would seem to be `None`, as there is _no_ path that exits the grid.
2. Rather than tracking only the seen _locations_, we'll want to track the seen
_positions_ -- with both location and direction -- so we can detect a loop if
the guard revisits a previously-seen position. We'll still want to _return_ only
the locations, though, so we can use a set comprehension to get each position's
grid point.

```py title="2024\day06\solution.py" ins={5-6} ins=" | None" ins="path: set[Position]" ins="{p.point for p in path}"
def track_guard(grid: Grid[str], guard: Position) -> set[GridPoint] | None:
    path: set[Position] = set()

    while guard.point in grid:
        if guard in path:
            return None
        path.add(guard)

        if grid.get(guard.next_point) == "#":
            guard = guard.rotate("CW")
        else:
            guard = guard.step()

    return {p.point for p in path}
```

Our `track_guard` function will now return `None` if the guard gets into an
infinite loop, and will otherwise act the same as before. At this point, it's a
good idea to assert that the set of seen points will not be `None` for our Part
1 solution.

```py title="2024\day06\solution.py" ins="solve" ins="tuple[int, int]" ins={11}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        guard = Position(
            point=next(k for k, v in grid.items() if v == "^"),
            facing=Direction.UP,
        )
        points_seen = track_guard(grid, guard)
        assert points_seen is not None

        ...  # TODO Add count-obstacle-placements code

        return len(points_seen), ...
```

Now we can try placing obstacles in the grid. An obstacle can be placed on any
empty tile (i.e. without a guard or another obstacle), so let's first try
brute-forcing all possible obstacle placements and tallying the ones that get
the guard stuck in a loop.

```py title="2024\day06\solution.py" ins={7-20} ins=/, (num_obstacle_placements)/
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        num_obstacle_placements = 0
        for obstacle_point in grid:
            # An obstacle can only be placed on an empty tile
            if grid[obstacle_point] != ".":
                continue

            # Try placing an obstacle here
            grid[obstacle_point] = "#"
            blocked_points = track_guard(grid, guard)
            # If the guard got stuck in a loop, tally this placement
            if blocked_points is None:
                num_obstacle_placements += 1
            # Un-place the obstacle
            grid[obstacle_point] = "."

        return len(points_seen), num_obstacle_placements
```

This brute-force approach works, but it takes almost a full minute to run on my
machine. A better approach would be to only try placing obstacles along the
guard's original path, as those points are the only ones the guard would run
into.

```py title="2024\day06\solution.py" ins="points_seen"
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        for obstacle_point in points_seen:
            ...

        ...
```

This already reduces the runtime to ~11.7 seconds on my machine -- a massive
improvement! But can we do _better_?

---

Whenever a new obstacle placement is tried, the guard has to walk along her
original path up to that obstacle, and it's only _afterwards_ that her path
diverges. So if `track_guard` returned the _positions_ along the guard's path,
instead of only the _locations_, perhaps the traversal of this path up to the
new obstacle could be done faster.

But how should we represent these positions? It's not exactly obvious which data
structure to use.

- The path positions must be in order from earliest to latest, which suggests
that we should use a `list` of `Position`s.
- Checking whether a path position was already seen should be fast, which
suggests that we should use a `set` of `Position`s.
- If we use a `list` to place the positions in order, we won't have fast
membership checking. But if we use a `set` to allow for fast membership
checking, we lose the ability to place them in order.[^both-list-and-set]

[^both-list-and-set]: We _could_ use both a `list` and a `set`, and update them
both in sync with each other, but it's a bit clunky.

In effect, what we need is some sort of "ordered set". Does such a data
structure exist in Python? Technically, it does: the humble `dict`.

- Checking whether an item with a certain key exists in a `dict` is very fast;
both `set`s and `dict`s use an object's "hash value" to check its membership.
- As of Python 3.7, `dict`s remember the order in which new keys are inserted.

So if we use the keys of a `dict` to store the path positions -- using `None` as
the associated value, because it doesn't matter -- we get the exact "ordered
set" behavior we want!

```py
>>> d = {}
>>> d["one"] = None
>>> d["two"] = None
>>> d["three"] = None
>>> d
{"one": None, "two": None, "three": None}
>>> list(d)
["one", "two", "three"]
```

We can use this knowledge to improve the runtime of our solution, but it'll take
a bit of refactoring.

First, we'll change `track_guard` so that it uses a `dict` to track positions
along the path, and returns those positions as a `list` (instead of the
locations as a `set`). As stated, these path positions will remain in the order
that they were inserted into the `dict`.

```py title="2024\day06\solution.py" ins={3-6,12,20} del={2,11,19} ins="list[Position]"
def track_guard(grid: Grid[str], guard: Position) -> list[Position] | None:
    path: set[Position] = set()
    # HACK This dict is being used as an "ordered set", so to speak. It
    # stores the positions in order (with values of None), and we can
    # quickly check whether it contains a certain position.
    path: dict[Position, None] = {}

    while guard.point in grid:
        if guard in path:
            return None
        path.add(guard)
        path[guard] = None

        if grid.get(guard.next_point) == "#":
            guard = guard.rotate("CW")
        else:
            guard = guard.step()

    return {p.point for p in path}
    return list(path)
```

Next, we'll tweak our Part 1 solution to leave this new path positions list as
is, and then use it to construct the `points_seen` set.

```py title="2024\day06\solution.py" ins=/(path) / ins={12}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        guard = Position(
            point=next(k for k, v in grid.items() if v == "^"),
            facing=Direction.UP,
        )
        path = track_guard(grid, guard)
        assert path is not None
        points_seen = {p.point for p in path}
        ...
```

Finally, we can implement the actual speedup. In Part 2, instead of starting
each gallivant from the guard's starting position, we can start from the path
position _just_ before the newly placed obstacle. We can find this position
using a `next()` expression involving our path list.

```py title="2024\day06\solution.py" ins={14-18} ins="blocked_path" ins=/, (blocked_guard)/
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        num_obstacle_placements = 0
        for obstacle_point in points_seen:
            # An obstacle can only be placed on an empty tile
            if grid[obstacle_point] != ".":
                continue

            # Try placing an obstacle here
            grid[obstacle_point] = "#"
            # NOTE Because the guard's path will be identical up to the
            # obstacle, we can start the guard directly before it.
            blocked_guard = next(
                p for p in path if p.next_point == obstacle_point
            )
            blocked_path = track_guard(grid, blocked_guard)
            # If the guard got stuck in a loop, tally this placement
            if blocked_path is None:
                num_obstacle_placements += 1
            # Un-place the obstacle
            grid[obstacle_point] = "."

        return len(points_seen), num_obstacle_placements
```

Believe it or not, this approach ends up considerably faster; the new runtime is
~5.7 seconds on my machine. I think that's about as good as I can do while still
keeping the code simple.
