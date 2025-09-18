---
year: 2023
day: 16
title: "The Floor Will Be Lava"
slug: 2023/day/16
pub_date: "2025-10-30"
# concepts: []
---
## Part 1

Another day, another grid puzzle. Time for me to use my [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
from [Day 10](/solutions/2023/day/10) again... but let's add some functionality
to it while we're at it.

One thing that's just as important as _moving_ in a direction is _changing_
direction. So I've taken the `Direction` class I showcased before, and added a
`rotate` method that takes a direction and rotates it
**C**ounter-**C**lock**W**ise or **C**lock**W**ise.

```py title="utils\grids.py" ins={3,11-13}
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

I've also created a `Position` class, which is basically a grid location
combined with a facing direction (along with a few convenience methods for
stepping forward and rotating). This turns out to be useful for today's puzzle,
where we're modeling beams of light.

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

As the beams bounce around the grid, they will either continue forward, change
direction, or split into multiple beams, based on the character they encounter
in the grid. Let's write the signature of a function for this, and we'll worry
about implementing it later.

```py title="2023\day16\solution.py"
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        ...  # TODO Add get-next-beams code
```

The solution we'll be using isn't too complicated; we'll simulate the beams of
light for as long as possible, until they either leave the grid or loop back to
a beam state we've seen before. Because beams can split, we store a `list` of
all the currently moving beams and process them one at a time.[^bfs-or-dfs] Once
every beam's path has been fully explored, we can tally up all the grid tiles
they've energized.

[^bfs-or-dfs]: The usual way we'd implement this kind of algorithm is with a BFS
([breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)),
but I've implemented it with a DFS ([depth-first search](https://en.wikipedia.org/wiki/Depth-first_search))
instead. Doing a DFS here removes the dependency on [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
that a BFS would usually need, and in this case the same answer is reached
either way.

```py title="2023\day16\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        seen: set[Beam] = set()
        # At top-left corner, facing right
        beams: list[Beam] = [Beam((0, 0), Direction.RIGHT)]
        while beams:
            current = beams.pop()
            if current in seen:
                continue
            seen.add(current)

            for next_beam in current.next_beams(grid[current.point]):
                if next_beam.point in grid:
                    beams.append(next_beam)

        # Count unique energized tiles
        return len({beam.point for beam in seen})
```

Now comes the part where we implement the beam-moving logic. We could implement
it with some giant `if`-`elif`-`else` chain, but I prefer using [`match`](https://peps.python.org/pep-0636/)
because it doesn't require us to repeat the value we're comparing against, and I
just overall like its syntax.[^match-nested]

[^match-nested]: The one drawback in my opinion is that `match` increases the
[nesting](https://pep20.org/#flat) level over an `if`-`elif`-`else` chain... but
eh, whaddya gonna do?

First, the easiest case: empty space. The beam of light will simply step forward
over empty space unaffected.

```py title="2023\day16\solution.py" ins={3-6}
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        match char:
            # Empty space: ignore
            case ".":
                return [self.step()]
            ...
```

Next, the splitters. If the beam runs into the pointy end of a splitter, it
steps forward unaffected like it does in empty space. But if it runs into the
flat side, the beam will split into two copies of itself: one rotated
counter-clockwise, and one rotated clockwise. (Note that I also have them `step`
forward after rotating, so the beam reaches a new tile.)

```py title="2023\day16\solution.py" ins={5-12}
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        match char:
            ...
            # Pointy end of splitter: ignore
            case "-" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.step()]
            case "|" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.step()]
            # Flat side of splitter: split
            case "-" | "|":
                return [self.rotate("CCW").step(), self.rotate("CW").step()]
            ...
```

Next, the mirrors. A horizontally-moving beam will turn counter-clockwise if it
hits a `/`, and clockwise if it hits a `\`; a vertically-moving beam will do the
opposite. (Note that I also have them `step` forward after rotating, so the beam
reaches a new tile.)

```py title="2023\day16\solution.py" ins={5-13}
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        match char:
            ...
            # Mirror: reflect
            case "/" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate("CCW").step()]
            case "/" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate("CW").step()]
            case "\\" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate("CW").step()]
            case "\\" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate("CCW").step()]
            ...
```

And finally, to ensure that we would see an [error](https://pep20.org/#errors)
if we failed to account for some character,[^exhaustive-match] we can raise an
error for any other situation.

[^exhaustive-match]: _And_ to make the type checker happy. Because it's not
happy unless a `match` statement is "exhaustive" -- i.e. handles all possible
patterns that the subject could match.

```py title="2023\day16\solution.py" ins={5-9}
class Beam(Position):
    def next_beams(self, char: str) -> list["Beam"]:
        match char:
            ...
            # Unknown char: error out
            case _:
                raise ValueError(
                    f"can't find next states from {self} and {char=}"
                )
```

This is now enough to give us our answer! And I got some useful additions to my
`grids` module out of it.

## Part 2

Part 2 requires us to run the beam-energizing function many times and get the
largest result. First, let's factor out the core of the function.

```py title="2023\day16\solution.py" del={4,7} ins={5,8,13-14}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def _solve(self, grid: Grid[str], start: Beam) -> int:
        seen: set[Beam] = set()
        beams: list[Beam] = [Beam((0, 0), Direction.RIGHT)]
        beams: list[Beam] = [start]
        ...

    def part_1(self) -> int:
        grid = parse_grid(self.input)
        # At top-left corner, facing right
        return self._solve(grid, Beam((0, 0), Direction.RIGHT))
```

Next, let's run our function for each tile on the boundary of our grid facing
inwards, then pass all the results to `max`. (Using `*` to unpack these
generators saves us from having to store anything.)

```py title="2023\day16\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_2(self) -> int:
        grid_height = len(self.input)
        grid_width = len(self.input[0])
        grid = parse_grid(self.input)

        return max(
            # At top, facing down
            *(
                self._solve(grid, Beam((0, col), Direction.DOWN))
                for col in range(grid_width)
            ),
            # At right, facing left
            *(
                self._solve(grid, Beam((row, grid_width - 1), Direction.LEFT))
                for row in range(grid_height)
            ),
            # At bottom, facing up
            *(
                self._solve(grid, Beam((grid_height - 1, col), Direction.UP))
                for col in range(grid_width)
            ),
            # At left, facing right
            *(
                self._solve(grid, Beam((row, 0), Direction.RIGHT))
                for row in range(grid_height)
            ),
        )
```

I don't know of any clever tricks to avoid all this brute-forcing for both
parts, but at least it made the code easier to write.
