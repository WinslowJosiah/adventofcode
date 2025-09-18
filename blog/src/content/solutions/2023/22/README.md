---
year: 2023
day: 22
title: "Sand Slabs"
slug: 2023/day/22
pub_date: "2025-11-17"
# concepts: []
---
## Part 1

A 3D physics simulation with falling bricks of sand? It's not as difficult as it
sounds -- especially because the physics rules are so greatly simplified, it'll
act more like Tetris than like [Not Tetris](https://stabyourself.net/nottetris2).

Let's quickly design a minimal `Brick` class.

- Each brick is made up of several "cubes", each of which have X, Y, and Z
coordinates. We can say that a `Cube` is a 3-tuple of `int`s, and each brick
will have a `set` of them (to ensure no two cubes share coordinates).[^list-of-cubes]
- It'll help to give each brick an ID, which we can just set to its `int` index
in the list of input bricks.
- Being able to get the lowest Z position of the brick will be useful when we
make each brick fall, so we can have it be a computed `property` which returns
an `int`.

[^list-of-cubes]: Technically we could make it a `list` of cubes -- which would
be a tad faster -- but then it'd be easier to make the mistake of duplicating
cubes.

```py title="2023\day22\solution.py"
from dataclasses import dataclass

type Cube = tuple[int, int, int]

@dataclass
class Brick:
    id_: int
    cubes: set[Cube]

    @property
    def lowest_z(self) -> int:
        return min(z for _, _, z in self.cubes)
    ...
```

Let's also create a `parse` function for parsing into a `Brick`, which can be a
method of `Brick` that we decorate with [`@classmethod`](https://docs.python.org/3/library/functions.html#classmethod).
(This means we'll be able to call it like `Brick.parse()`.)

:::attention
Instead of having an instance of the class (commonly called `self`) as the first
argument, `classmethod`s have _the class itself_ (commonly called `cls`) as the
first argument.

This makes them useful for giving a class an alternative constructor, like we do
here. But keep in mind that we can't change anything about `self` in such a
function, as that isn't passed to a `classmethod`.
:::

```py title="2023\day22\solution.py"
from itertools import product
from typing import Self

@dataclass
class Brick:
    ...
    @classmethod
    def parse(cls, id_: int, line: str) -> Self:
        start, end = (point.split(",") for point in line.split("~"))
        dim_ranges = [range(int(l), int(r) + 1) for l, r in zip(start, end)]
        cubes = {(x, y, z) for x, y, z in product(*dim_ranges)}
        return cls(id_, cubes)
```

This looks a bit dense, but it's not _too_ bad. Let's break it down:

1. The two opposite ends of the brick, which I've called `start` and `end`, are
separated by a `~`, and the coordinates are separated by commas. We can use
[`str.split`](https://docs.python.org/3/library/stdtypes.html#str.split) to take
care of them.
2. The coordinates can be thought of as the start and stop points of (inclusive)
ranges over each dimension (X/Y/Z), and cubes will exist at each coordinate
inside these ranges. We can use [`zip`](https://docs.python.org/3/library/functions.html#zip)
to loop over each pair of endpoints, and build each range from those.
3. [`itertools.product`](https://docs.python.org/3/library/itertools.html#itertools.product)
will loop over every cube whose coordinates are inside all of these ranges --
similar to a nested `for` loop.
4. Finally, we return a new instance of the class with the proper `id_` and
`cubes` attributes.

The first thing we'll do is sort the bricks by their lowest Z coordinate, so
that when we make them fall, we can make the lower bricks fall before the higher
ones. We can do the sorting and parsing at the same time with the [`sorted`](https://docs.python.org/3/library/functions.html#sorted)
function.

```py title="2023\day22\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        # Sort bricks from lowest to highest
        bricks = sorted(
            (Brick.parse(i, line) for i, line in enumerate(self.input)),
            key=lambda b: b.lowest_z,
        )
        ...
```

Now we'll make the bricks fall down as far as they can go. We could try bringing
them down one Z value at a time until they settle, but an interesting thing we
can do instead is _teleport_ them to the lowest point they can reach.[^hard-drop]

[^hard-drop]: In Tetris terms, it's like doing a "hard drop" instead of a "soft
drop".

We'll create a [heightmap](https://en.wikipedia.org/wiki/Heightmap) to keep
track of the height of the highest cube at every X/Y location. Imagine you're
looking down at the floor, and each cube has a number indicating how high it is;
the heightmap entry at each X/Y location will be the only number you can see
there that isn't being blocked. Here's a crude ASCII-art illustration of the
concept, using the bricks from the sample input:

```text
Initial heightmap:
  x
 ###     000
y### --> 000
 ###     000

Brick A (3 long):
  x
 #A#     010
y#A# --> 010
 #A#     010

Brick B (3 wide):
  x
 BBB     222
y#A# --> 010
 #A#     010

Brick C (3 wide):
  x
 BBB     222
y#A# --> 010
 CCC     222

Brick D (3 long):
  x
 DBB     322
yDA# --> 310
 DCC     322

Brick E (3 long):
  x
 DBE     323
yDAE --> 313
 DCE     323

Brick F (3 wide):
  x
 DBE     323
yFFF --> 444
 DCE     323

Brick G (2 tall):
  x
 DBE     323
yFGF --> 464
 DCE     323
```

The bricks don't have any strange and complex shapes, so the lowest Z position
of a falling brick will be just above the highest heightmap entry it covers. We
can do some math to the Z position of the brick's cubes to make it fall there,
then we can use their new heights to update the heightmap.

```py title="2023\day22\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        # NOTE The default height here is 0, meaning the ground.
        height_map: dict[tuple[int, int], int] = defaultdict(int)
        # Make each brick fall until it hits the ground or another brick
        for brick in bricks:
            target_z = max(height_map[x, y] + 1 for x, y, _ in brick.cubes)
            delta_z = brick.lowest_z - target_z
            brick.cubes = {(x, y, z - delta_z) for x, y, z in brick.cubes}
            # Update the height map with the new settled brick
            for x, y, z in brick.cubes:
                height_map[x, y] = max(height_map[x, y], z)
        ...
```

Now that all of the bricks have fallen, we need to figure out which bricks are
supporting which other bricks. Each brick will be supporting any brick that sits
just above it, and will be supported by any brick that sits just below it. (I
keep track of both the "supports" and "supported-by" relations, because having
both helped me in solving the puzzle.)

```py title="2023\day22\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        cube_to_brick_id = {
            cube: brick.id_
            for brick in bricks
            for cube in brick.cubes
        }
        # Find out which bricks support which other bricks
        supports: dict[int, set[int]] = {}
        supported_by: dict[int, set[int]] = defaultdict(set)
        for brick in bricks:
            cubes_above = {(x, y, z + 1) for x, y, z in brick.cubes}
            bottom_id = brick.id_
            top_ids = {
                top_id
                for cube in cubes_above
                if (top_id := cube_to_brick_id.get(cube)) is not None
                and top_id != bottom_id
            }
            # NOTE It's helpful to have a mapping in both directions.
            supports[bottom_id] = top_ids
            for top_id in top_ids:
                supported_by[top_id].add(bottom_id)
        ...
```

Which bricks can be safely disintegrated without causing any other bricks to
fall? To answer this question, I found it easier to ask the opposite question --
which bricks _can't_ be safely disintegrated -- and subtract that answer from
the total number of bricks.

The bricks that can't be safely disintegrated are the "load-bearers" -- the
bricks that are the sole supporters of some other "top brick". In other words,
if a "top brick" is supported by only one "bottom brick", that bottom brick is a
"load-bearer". These load-bearers can be found with a set comprehension.

```py title="2023\day22\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        # If a top brick is only supported by one bottom brick, that
        # bottom brick is a "load bearer" and cannot be safely removed
        load_bearers = {
            bottom_id
            for _, bottom_ids in supported_by.items()
            for bottom_id in bottom_ids
            if len(bottom_ids) == 1
        }
        return len(bricks) - len(load_bearers)
```

This gets us to a very quick answer... though I have to admit, it was a bit
confusing at first to think of the proper criteria for being a "load-bearer".

## Part 2

We'll need all the brick-related data structures from Part 1 for our Part 2
solution. So let's make it into a unified `solve` function.

```py title="2023\day22\solution.py" ins="solve" ins="tuple[int, int]" ins="num_removable_bricks ="
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        num_removable_bricks = len(bricks) - len(load_bearers)
        ...
```

We're asked to imagine disintegrating each brick, and count the other bricks
that would then be caught in a chain reaction of falling bricks. And as it turns
out, the "load-bearers" we found in Part 1 are precisely the bricks that would
cause such a chain reaction, so we could just loop through all the load-bearers
instead of doing the work of looping through every brick.

We can use a `deque` to keep track of bricks involved in the chain reaction,
adding the top bricks that each bottom brick supports. Once we've found every
brick that's involved in the chain reaction, we add it to a running total --
remembering _not_ to count the original brick that we've disintegrated.

```py title="2023\day22\solution.py"
from collections import deque
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...
        num_falling_bricks = 0
        # For each "load bearer" brick
        for brick_id in load_bearers:
            removed = {brick_id}
            # Find all other bricks that would fall if it were removed
            queue = deque(supports[brick_id])
            while queue:
                other_id = queue.popleft()
                if other_id in removed:
                    continue
                # If we've removed all supporters of this brick, it will
                # fall; remove it too, and check the bricks it supports
                if supported_by[other_id].issubset(removed):
                    removed.add(other_id)
                    queue.extend(supports[other_id])
            # NOTE We subtract 1 here because we don't count the initial
            # brick that was removed.
            num_falling_bricks += len(removed) - 1

        return num_removable_bricks, num_falling_bricks
```

I wish I were talented enough to make a visualization of this, but
[plenty of other folks](https://reddit.com/r/adventofcode/search/?q=%222023+day+22%22+flair%3AVisualization)
have done so themselves. I think this day in particular is a cool one to
visualize; if you're having trouble understanding what's going on, perhaps
looking at one of those visualizations might help.
