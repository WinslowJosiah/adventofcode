---
year: 2024
day: 15
title: "Warehouse Woes"
slug: 2024/day/15
pub_date: "2026-06-29"
# concepts: []
---
## Part 1

Another day, another grid puzzle. And I'm _very_ interested to visualize this
one; this reminds me a lot of [Sokoban](https://en.wikipedia.org/wiki/Sokoban).

I'll be using the same custom [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py)
I used on Days [4](/solutions/2024/day/4), [6](/solutions/2024/day/6), [8](/solutions/2024/day/8),
[10](/solutions/2024/day/10), and [12](/solutions/2024/day/12), so look at those
writeups to see how it works. Here, I'll want to create a grid _without_ the `#`
characters, so the only tiles in the grid are the ones you could potentially
walk on.

```py title="2024\day15\solution.py"
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_grid = self.input[0].splitlines()
        num_rows, num_cols = len(raw_grid), len(raw_grid[0])
        grid = parse_grid(raw_grid, ignore_chars="#")
        ...
```

Visualizing the grid will help when debugging our solution, and thankfully it's
super simple to write a function for it. We can loop over each row and column
and print each tile one by one (using the `end` argument of [`print`](https://docs.python.org/3/library/functions.html#print)
to omit the newline between each character of a row).

```py title="2024\day15\solution.py" {13}
def print_grid(grid: Grid[str], num_rows: int, num_cols: int):
    for r in range(num_rows):
        for c in range(num_cols):
            print(grid.get((r, c), "#"), end="")
        print()

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        raw_grid = self.input[0].splitlines()
        num_rows, num_cols = len(raw_grid), len(raw_grid[0])
        grid = parse_grid(raw_grid, ignore_chars="#")
        print_grid(grid, num_rows, num_cols)
        ...
```

If we test this function out on our example grid, we get an output that looks
like this. This is how I will visualize the grid after each step.

```text
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#.O@...O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########
```

Looks awesome! Now to write the rest of today's solution.

In my `grids` module, I have some helper classes and functions that deal with
grid coordinates, directions, and movement. I'm able to use them here to easily
implement the simplest case: movement through empty space. If we're moving into
a wall (i.e. onto a position that's not in the grid), we do nothing; otherwise,
we perform the move (where the place we're going becomes a `@`, and the place we
started on becomes a `.`).

```py title="2024\day15\solution.py" /(\\.\\.\\.)  #/
# Move characters + direction offsets of this move
MOVE_OFFSETS = {
    ">": Direction.RIGHT.offset,
    "v": Direction.DOWN.offset,
    "<": Direction.LEFT.offset,
    "^": Direction.UP.offset,
}
...

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        loc = next(k for k, v in grid.items() if v == "@")
        moves = self.input[1].replace("\n", "")

        for move in moves:
            offset = MOVE_OFFSETS[move]
            # Do nothing if moving into a wall
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            ...  # TODO Add maybe-push-boxes code

            # Move the robot
            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc
        ...
```

This works for movement, but it ends up removing the `O` boxes when we walk into
them. We'll want to push a box when we move into one, and the box should end up
moving into the space behind it if it's empty; however, if there's _not_ empty
space behind the box, we're pushing it into a wall, and so we should skip this
move entirely with `continue`. Let's implement that quickly.

```py title="2024\day15\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        for move in moves:
            ...
            # If pushing a box
            if grid[next_loc] == "O":
                # Find the tile behind the box we're pushing
                next_in_dir = add_points(next_loc, offset)

                # If empty space is behind this box, push the box;
                # otherwise, cancel the move
                if grid.get(next_in_dir) in grid:
                    grid[next_in_dir] = "O"
                else:
                    continue
            ...
        ...
```

Good news: now we're able to push single boxes! Bad news: we're not able to push
_groups_ of boxes. But this can be fixed by looking at _multiple_ tiles behind
the box, instead of only one. We can use a `while` loop here to scan past the
group of boxes until we reach some non-box tile (empty space, or a wall).

```py title="2024\day15\solution.py" ins="end of the group of boxes" ins=/(next_in_dir),/ ins=/(group), push the (group)/ ins={12-13,19-21}
...

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        for move in moves:
            ...
            # If pushing a box
            if grid[next_loc] == "O":
                # Find the end of the group of boxes we're pushing
                next_in_dir = next_loc
                while grid.get(next_in_dir) == "O":
                    next_in_dir = add_points(next_in_dir, offset)

                # If empty space is behind this group, push the group;
                # otherwise, cancel the move
                if grid.get(next_in_dir) in grid:
                    # NOTE Because each box is identical, we can just
                    # place a box behind the group to get the same
                    # result as pushing it.
                    grid[next_in_dir] = "O"
                else:
                    continue
            ...
        ...
```

:::note
You might think that we need to change how we actually _move_ the boxes in order
to move the whole group instead of a single box... but believe it or not, this
code actually produces the correct behavior on its own! This might be a bit
surprising, because we're just stepping over the box in the front and placing a
box in the back, just like we did in the case of one box.

The reason this works with multiple boxes is that we're pushing lines of
_identical_ boxes; visually, the only thing that changes after a push is that
there is one fewer box in the front and one more box in the back.

```text
line of distinguishable boxes
@ABC.
after a > move (shifting from front to back)
.@BCA
after a > move (properly pushing)
.@ABC

line of identical boxes
@OOO.
after a > move (shifting from front to back)
.@OOO
after a > move (properly pushing)
.@OOO
```

As you can see, with identical boxes, this gives us the exact same result as
shifting over every box in the group, and we only had to move _one_ box!
:::

With the movement and pushing working correctly, we can now calculate the sum of
the boxes' "GPS coordinates": 100 times the row index, plus the column index,
for each box in the grid.

```py title="2024\day15\solution.py"
...

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        return sum(
            100 * row + col
            for (row, col), char in grid.items()
            if char == "O"
        )
```

If you solve this while printing out the grid at each step (with a call to
[`time.sleep`](https://docs.python.org/3/library/time.html#time.sleep) to slow
it down enough to see), you get a useful and fun visualization of the robot as
it steps through the grid and pushes the boxes. It's hard not to get mesmerized
by it... somewhat like a real game of Sokoban.

## Part 2

Now the entire grid is wider, and so are the boxes. Having each box be two tiles
instead of one will make the simulation harder, but I'm confident that we can
make the necessary changes while keeping the general simulation process the
same.

So I'll first be factoring out our Part 1 solution into its own function, and
giving it the original grid for Part 1 and the wider grid for Part 2.

```py title="2024\day15\solution.py" ins={5,11,13-22}
...
class Solution(StrSplitSolution):
    ...

    def _solve(self, raw_grid: list[str], moves: Iterable[str]) -> int:
        ...  # Part 1 code from before

    def part_1(self) -> int:
        raw_grid = self.input[0].splitlines()
        moves = self.input[1].replace("\n", "")
        return self._solve(raw_grid, moves)

    def part_2(self) -> int:
        wide_table = str.maketrans({
            "#": "##",
            "O": "[]",
            ".": "..",
            "@": "@.",
        })
        raw_grid = self.input[0].translate(wide_table).splitlines()
        moves = self.input[1].replace("\n", "")
        return self._solve(raw_grid, moves)
```

:::tip
To create the wide version of the grid, we need to replace each individual
character with its wide version. But rather than string together[^string-together]
a bunch of calls to [`str.replace`](https://docs.python.org/3/library/stdtypes.html#str.replace),
we can use the lesser-known [`str.translate`](https://docs.python.org/3/library/stdtypes.html#str.translate)
and [`str.maketrans`](https://docs.python.org/3/library/stdtypes.html#str.maketrans)
methods to make that process more efficient and less error-prone.

Basically, you can use `str.maketrans` to create a "translation table", which
will represent substitutions you want to make to single characters. This
translation table can then be passed to a string's `translate` method to perform
those substitutions all at once.

```py
>>> table = str.maketrans({
...     "&": "&amp;",
...     ">": "&gt;",
...     "<": "&lt;",
... })
>>> s = "HTML uses tags like <b> & <i>"
>>> s.translate(table)
'HTML uses tags like &lt;b&gt; &amp; &lt;i&gt;'
```

For a more comprehensive overview of `str.translate` and `str.maketrans`,
[this post from Mathspp](https://mathspp.com/blog/pydonts/string-translate-and-maketrans-methods)
does a very good job of explaining them in detail.
:::

[^string-together]: No pun intended.

Most of the code from Part 1 can stay the same, except for two changes to
accommodate both parts:

1. The way boxes are pushed needs to be changed; while in Part 1 we could get
away with something super simple, in Part 2 we actually need to detect and shift
the boxes we're pushing. (This will be a bit complex, but as they say, that's
[better than complicated](https://pep20.org/#complex).)
2. The GPS coordinate sum should be totaled for both the `O` characters of thin
boxes and the `[` characters of wide boxes.

```py title="2024\day15\solution.py" {"1":17-18} {"2":28}
...
class Solution(StrSplitSolution):
    ...

    def _solve(self, raw_grid: list[str], moves: Iterable[str]) -> int:
        num_rows, num_cols = len(raw_grid), len(raw_grid[0])
        grid = parse_grid(raw_grid, ignore_chars="#")
        loc = next(k for k, v in grid.items() if v == "@")

        for move in moves:
            move_offset = MOVE_OFFSETS[move]
            # Do nothing if moving into a wall
            if (next_loc := add_points(loc, move_offset)) not in grid:
                continue

            # If pushing a box
            if grid[next_loc] in "O[]":
                ...  # TODO Add push-wide-boxes code

            # Move the robot
            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc

        return sum(
            100 * row + col
            for (row, col), char in grid.items()
            if char in "O["
        )
```

Pushing the boxes will be done in two phases: detection and shifting. First
we'll detect which tiles need to be moved by scanning from closest to farthest,
and then we'll need to shift those tiles in the right direction.

The detection phase will be the harder one to implement, so let's imagine for
now that we've made a function for it; once we have the resulting list of tile
locations to shift, the shifting phase will begin.

- An empty list (i.e. _no_ tiles being shifted) will mean we're blocked, and we
should cancel the move.
- Otherwise, we'll want to shift each tile in the list forward, starting from
the farthest one -- i.e. in _reverse_ order, because the list will already be in
order from closest to farthest. We can iterate through the list in reverse order
with [`reversed`](https://docs.python.org/3/library/functions.html#reversed).

```py title="2024\day15\solution.py" ins={11-19} "gather_pushed_tiles"
...
class Solution(StrSplitSolution):
    ...

    def _solve(self, raw_grid: list[str], moves: Iterable[str]) -> int:
        ...
        for move in moves:
            ...
            # If pushing a box
            if grid[next_loc] in "O[]":
                pushed_tiles = gather_pushed_tiles(grid, loc, move)
                # If this move doesn't push any tiles, cancel the move
                if not pushed_tiles:
                    continue

                # Push the tiles in the group from farthest to closest
                for p in reversed(pushed_tiles):
                    grid[add_points(p, move_offset)] = grid[p]
                    grid[p] = "."
            ...
        ...
```

Now to implement the detection phase. The case of moving left or right will be
easier to handle; in fact, we can handle this very similarly to how we handled
pushing boxes in Part 1! Starting from the tile in front of us, we'll gather
each box tile we see into a list called `pushed_tiles`, until we reach a non-box
tile. Based on this non-box tile we see, we'll do one of two things:

- If that tile is inside the grid, it must be an empty tile; we can return the
`pushed_tiles` list as-is.
- If that tile is outside the grid, it must be a wall; we're being blocked, and
we should instead return an empty list of pushed tile locations.

```py title="2024\day15\solution.py"
def gather_pushed_tiles(
        grid: Grid[str],
        loc: GridPoint,
        move: str,
) -> list[GridPoint]:
    """
    Gather the locations of tiles that will be pushed by this move at
    this location in this grid; return those tile locations from closest
    to farthest.

    Assumes that this move would overlap a box tile.
    """
    move_offset = MOVE_OFFSETS[move]
    next_loc = add_points(loc, move_offset)

    # If pushing a box left/right (the simpler case)
    if move in "><":
        # Gather the group of box tiles we're pushing
        next_in_dir = next_loc
        pushed_tiles: list[GridPoint] = []
        while grid.get(next_in_dir, "#") in "O[]":
            pushed_tiles.append(next_in_dir)
            next_in_dir = add_points(next_in_dir, move_offset)

        # If moving into empty space, we're pushing the gathered tiles;
        # otherwise, we're blocked and pushing no tiles
        return pushed_tiles if next_in_dir in grid else []
    ...
```

Finally, we must handle the case of moving up or down -- by far the hardest
case to implement, because the tiles of the wider boxes have to act like they're
connected. To handle this, I created a `dict` that maps the box characters (`O`,
`[`, and `]`) to the offsets of all the tiles belonging to that box. (In fact,
while I was at it, I changed all my box-character checks to check whether a
character was in this `dict`; it's more [readable](https://pep20.org/#readability)
and the intent is much more [explicit](https://pep20.org/#explicit).)

```py title="2024\day15\solution.py" del={17,31} ins={1-6,18,32}
# Box characters + offsets to the tiles of the box
BOX_OFFSETS: dict[str, list[GridPoint]] = {
    "O": [(0, 0)],
    "[": [(0, 0), Direction.RIGHT.offset],
    "]": [(0, 0), Direction.LEFT.offset],
}

def gather_pushed_tiles(
        grid: Grid[str],
        loc: GridPoint,
        move: str,
) -> list[GridPoint]:
    ...
    # If pushing a box left/right (the simpler case)
    if move in "><":
        ...
        while grid.get(next_in_dir, "#") in "O[]":
        while grid.get(next_in_dir) in BOX_OFFSETS.keys():
            ...
        ...
    ...

class Solution(StrSplitSolution):
    ...

    def _solve(self, raw_grid: list[str], moves: Iterable[str]) -> int:
        ...
        for move in moves:
            ...
            # If pushing a box
            if grid[next_loc] in "O[]":
            if grid[next_loc] in BOX_OFFSETS.keys():
                ...
            ...
        ...
```

How do we handle pushing boxes up or down? This is a difficult question, but the
approach I landed on is similar to [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search);
we can find the box we're pushing, find all the boxes _that_ box is pushing,
find all the boxes _those_ boxes are pushing, and so on through each row of
boxes in front of us. Step by step, this means we must:

1. Find the box tile we're pushing, and all connected tiles. This will be the
first row of pushed boxes.
2. For each pushed box tile from the previous row, find the tiles _they're_
pushing, and all connected tiles. This will be the next row of pushed boxes.
3. If any box tile would get pushed into a wall, we're blocked, and we should
cancel the move.
4. Keep track of the box tiles from this row. If there are no more box tiles
being pushed, we're done detecting the pushed box tiles, and we should return
those tiles; otherwise, repeat from step 2.

A good choice to store the pushed rows of tiles is a list of lists of tiles; we
can flatten this nested list of tiles once we need to return the pushed tiles.

```py title="2024\day15\solution.py" {"1":13-20} {"2":23-31} {"3":33-35} {"4":37-46}
def gather_pushed_tiles(
        grid: Grid[str],
        loc: GridPoint,
        move: str,
) -> list[GridPoint]:
    ...
    # If we're here, we're pushing a box up/down
    # NOTE Our vertical push could cause a chain reaction of boxes
    # pushing other boxes. Thus, we'll check each row from closest to
    # farthest for tiles that will be pushed; each row of pushed tile
    # positions will be appended to pushed_rows.

    # The box tile in front of us, and every tile it's connected to,
    # will be pushed
    pushed_rows = [
        [
            add_points(next_loc, box_offset)
            for box_offset in BOX_OFFSETS[grid[next_loc]]
        ],
    ]
    # Find the rest of the group of boxes we're pushing
    while True:
        # Each pushed box tile from the last row should push the tile in
        # front of it...
        next_row = {add_points(p, move_offset) for p in pushed_rows[-1]}
        # ...and the tiles that those tiles are connected to
        next_row |= {
            add_points(p, box_offset)
            for p in next_row
            for box_offset in BOX_OFFSETS.get(grid.get(p, "#"), [])
        }

        # If moving into a wall, we're blocked and pushing no tiles
        if any(p not in grid for p in next_row):
            return []

        # If moving into more boxes, their tiles will also be pushed
        if (next_tiles := [
            p for p in next_row
            if grid[p] in BOX_OFFSETS.keys()
        ]):
            pushed_rows.append(next_tiles)
        # Otherwise, we're done looking for boxes; gather the tiles from
        # every row and return them
        else:
            return [tile for row in pushed_rows for tile in row]
```

All the necessary parts are in place now -- even though we worked on them
backwards out of convenience. I'd definitely have done this a different way if
the boxes also got taller, or if they ended up being different sizes... but I
think this approach is pretty good nonetheless. Of course, it's _all_ worth it
to be able to see our debug visualization code working for Part 2 as well;
that's my favorite part of today's puzzle!
