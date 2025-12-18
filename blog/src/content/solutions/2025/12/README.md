---
year: 2025
day: 12
title: "Christmas Tree Farm"
slug: 2025/day/12
pub_date: "2025-12-12"
# concepts: []
---
## Part 1

It is now Day 12, and the final day of Advent of Code! Fittingly, we now have to
put presents under various Christmas trees, in a manner similar to Tetris... or,
more precisely, the [pentomino tiling puzzle](https://en.wikipedia.org/wiki/Pentomino#Tiling_puzzle_(2D))
it was based on.

The shapes of the presents all happen to fit in a 3x3 grid (a fact which we can
`assert` with some effort). For now, the first thing we can do is count the
number of `#` tiles in each shape, which will become useful.

```py title="2025\day12\solution.py"
...

class Solution(TextSolution):
    def part_1(self) -> int:
        SHAPE_WIDTH = SHAPE_HEIGHT = 3
        *raw_shapes, raw_regions = self.input.split("\n\n")

        # Get the number of tiles in each shape
        shape_num_tiles: list[int] = []
        for raw_shape in raw_shapes:
            _, *grid = raw_shape.splitlines()
            assert len(grid) == SHAPE_HEIGHT
            assert all(len(row) == SHAPE_WIDTH for row in grid)
            shape_num_tiles.append(
                sum(ch == "#" for row in grid for ch in row)
            )
        ...
```

Our loop through the regions under each Christmas tree will look something like
this. Something with [`re.findall`](https://docs.python.org/3/library/re.html#re.findall)
makes quick work of extracting the numbers we need from each line. But the main
thing to do is figure out if the region can be filled with presents; if it can,
we will add it to a tally.

```py title="2025\day12\solution.py" /if (\\(\\))/
import re

class Solution(TextSolution):
    def part_1(self) -> int:
        ...
        total = 0
        for raw_region in raw_regions.splitlines():
            width, height, *shape_quantities = (
                map(int, re.findall(r"\d+", raw_region))
            )

            if ():  # TODO Add is-region-fillable code
                total += 1

        return total
```

Unfortunately for us, such a tiling problem is [NP-complete](https://en.wikipedia.org/wiki/NP-completeness)
-- solutions are easy to _verify_, but hard to _find_. Are there any cases where
we can easily verify that a solution exists?

Well, all of our presents are 3x3, so we can fit at least `width // 3` of them
along the region's width, and at least `height // 3` of them along its height.
If we multiply those two numbers together, _at least that many_ presents will
definitely fit in the region. So if we have that many presents or less, there is
definitely a solution, and we can immediately add 1 to the tally and move on.

```py title="2025\day12\solution.py"
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...
        for raw_region in raw_regions.splitlines():
            ...
            # If this amount of presents definitely fits, add to tally
            max_presents_lower_bound = (
                (width // SHAPE_WIDTH) * (height // SHAPE_HEIGHT)
            )
            num_presents = sum(shape_quantities)
            if num_presents <= max_presents_lower_bound:
                total += 1
                continue
            ...
```

Next, are there any cases where we can easily verify that a solution _doesn't_
exist? Certainly, if the presents take up more tiles than there are in the
region, there will be no solution; thus, we can immediately move on.

```py title="2025\day12\solution.py"
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...
        for raw_region in raw_regions.splitlines():
            ...
            # Skip if lower bound of tile count won't fit in the region
            num_tiles_lower_bound = sum(
                tiles * quantity
                for tiles, quantity in zip(shape_num_tiles, shape_quantities)
            )
            region_num_tiles = width * height
            if num_tiles_lower_bound > region_num_tiles:
                continue

            assert False, "shape packing is complicated"
        ...
```

I went ahead and added an `assert False` statement afterwards, which will raise
an error if both checks fail. Of course, our checks are too basic to cover
_every_ possible case that could happen -- in fact, they don't even cover every
case in the sample input! So how early will our check fail for the full puzzle
input? Let's run our code now and see...

```cmd title=""
C:\Users\josia\Documents\Python\adventofcode>py aoc.py -y 2025 -d 12
# 2025\day12\input.txt

## Solutions for Advent of Code 2025 Day 12
### Part 1
555
```

...oh. Hm. Somehow our two basic checks were enough.

That was anticlimactic -- and I don't really like solutions that don't work in
general cases -- but hey, it was either this, or figure out how to efficiently
do shape-packing. I'll take it.

## Part 2

The 12 Days of Advent of Code are now over! Perhaps the difficulty curve could
use some tuning, but other than that, this was a nice season.

If you don't have all 23 stars by now, I recommend going back to
[the previous solutions](/solutions/2025) and seeing what you missed. [Day 9](/solutions/2025/day/9)
and [Day 10](/solutions/2025/day/10) were especially tricky for me; my personal
times for those days were the highest by far.

And if you do have all 23 stars, congratulations on completing Advent of Code
2025!

### The Brahminy

Even though I've obtained every single star from completing the puzzles, I'm not
quite done yet.

Over the 12 days of AoC 2025, I'd been chipping away at a special program that
solves _every_ AoC 2025 puzzle in a _single_ line of Python. I'm calling it
[The Brahminy](https://github.com/WinslowJosiah/adventofcode/blob/main/solutions/2025/brahminy.py)
-- after one of the smallest varieties of snake. It's entirely impractical to do
it this way, but I'm doing it as a challenge to myself, and I've personally been
having fun writing it.

I was able to finish it by December 13th; it has solutions to every 2025 puzzle
from Day 1 to Day 12. If you're into that sort of thing, be sure to check it
out!
