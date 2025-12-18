---
year: 2025
day: 8
title: "Playground"
slug: 2025/day/8
pub_date: "2025-12-08"
# concepts: []
---
## Part 1

Today's puzzle has taken me the longest to figure out so far this year -- mainly
due to a bad choice of data structure. Looking at [the Reddit solution thread](https://reddit.com/comments/1ph3tfc),
the silver bullet seems to be a specialized [disjoint-set data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
(also known as "union-find"), so let's look at a canonical example of one.

A disjoint-set data structure is made for storing disjoint (non-overlapping)
sets of items, which we can use here to store the connected circuits of junction
boxes. The particular way we'll do this is with a **forest** -- so called
because it is a collection of [trees](https://en.wikipedia.org/wiki/Tree_(graph_theory)).[^i-like-that-name]

[^i-like-that-name]: I like that name. It's just the right amount of clever.

Each tree stores the items of one of the sets; the idea is that trees can be
combined very simply, by setting the root of one tree to be a descendant of the
other, allowing for a simple set `union` operation. Of course, to do anything
with the root of a tree, you must be able to _find_ its root; the operation
which does this is called `find`. (Hence the name "union-find".)

My implementation of this data structure is pretty standard. The only things it
keeps track of are each item's `parent` (in its corresponding tree) and each
set's `size` (which is stored only for the roots of each tree). Here's what I do
for the `union` and `find` functions -- and a small optimization I make for both
of them:

1. For `find`, I use a simple recursive algorithm to find a tree's root; the
base case is an item that already _is_ a root (which is simply returned), and
the recursive case calls `find` on the item's parent.

    Once I find the root, I make it that item's new parent -- an optimization
    known as "path compression", which speeds up future `find` calls.
2. For `union`, I use `find` to find the roots of both trees I'm merging, set
one root as the parent of the other, and update the stored sizes to reflect the
merge.

    But the choice of which root should be the root of the merged tree is
    important, as many successive bad choices could lead to an excessively tall
    tree. One way to mitigate this is "union by size", a strategy that always
    chooses the root with more descendants. Luckily, we already keep track of
    the tree sizes, so we can use them directly to make this choice.

```py title="2025\day08\solution.py"
from collections import Iterable

class UnionFind[T]:
    def __init__(self, items: Iterable[T]):
        items_list = list(items)
        # NOTE An item is "its own parent" if and only if it is a root.
        self.parent = {item: item for item in items_list}
        # Track the size of each tree at its root
        self.size = {item: 1 for item in items_list}

    def find(self, item: T) -> T:
        # Compress the path to the root
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        # Now the item's "parent" will be the root of its set
        return self.parent[item]

    def union(self, item1: T, item2: T):
        # Find the roots of both sets
        root1, root2 = self.find(item1), self.find(item2)
        # Do nothing if both sets are already the same
        if root1 == root2:
            return

        # Ensure root1 is the one with more descendants
        # NOTE This merging strategy is called "union by size", and it
        # helps keep the tree height low.
        if self.size[root1] < self.size[root2]:
            root1, root2 = root2, root1
        # Make root1 the new root and update its stored size
        self.parent[root2] = root1
        self.size[root1] += self.size[root2]
        # root2 is no longer a root, so it shouldn't store a size
        del self.size[root2]

    @property
    def set_sizes(self) -> list[int]:
        return list(self.size.values())
```

(I also include a `set_sizes` property, because we need this information for
this specific puzzle.)

Now that we have a `UnionFind` class, the puzzle becomes almost trivial. So
let's implement everything else.

---

First, input parsing. This can be done rather simply, with each junction box
being represented as a `tuple` of its coordinates.

```py title="2025\day08\solution.py"
...

type Box = tuple[int, ...]
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        boxes: list[Box] = [
            tuple(map(int, line.split(","))) for line in self.input
        ]
        ...
```

Next, we need to take every pair of boxes and sort them by their straight-line
distance (aka [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance)).
This can also be done simply, using [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
to get the pairs, [`math.dist`](https://docs.python.org/3/library/math.html#math.dist)
to get their Euclidean distance, and [`sorted`](https://docs.python.org/3/library/functions.html#sorted)
to perform the sort.

```py title="2025\day08\solution.py" ins=", Sequence" ins={1-2}
from itertools import combinations
from math import dist
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        # Sort each pair by their Euclidean distance to each other
        pairs = sorted(combinations(boxes, 2), key=lambda pair: dist(*pair))
        ...
```

Once we have each pair sorted by distance, we will call our `UnionFind.union`
function on the first 1,000 pairs (or 10 pairs for the testing data).[^testing]

[^testing]: In Advent of Code, occasionally the test cases will have different
parameters or behave differently from the full puzzle input; this is one of
those days. To work around this, my solution template allows me to use the
`self.testing` attribute to check whether or not I'm running a solution on the
testing data.

```py title="2025\day08\solution.py" ins=", prod"
from math import dist, prod
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        uf = UnionFind(boxes)
        num_initial_pairs = 10 if self.testing else 1000

        # Make each connection from closest to farthest
        for box1, box2 in pairs[:num_initial_pairs]:
            uf.union(box1, box2)

        return prod(sorted(uf.set_sizes, reverse=True)[:3])
```

To get the sizes of the largest three sets, we can sort them in reverse and
slice the result; passing them to [`math.prod`](https://docs.python.org/3/library/math.html#math.prod)
gives us their product. Not a tall task at all when using `UnionFind`!

## Part 2

Once you can verify that you have Part 1 correct, you're probably going to
figure out Part 2 rather quickly. All it takes to turn the solution into a
unified `solve` function is a few changes.

- Instead of looking at the first 1,000 pairs, we want to keep looking at pairs
until we get answers for both Parts 1 and 2. (We can just calculate Part 1's
answer the moment we reach the 1,000th pair.)
- Once every box is connected into a single circuit, the `UnionFind.set_sizes`
property will return a list with only one item; at that point, we can calculate
Part 2's answer.

```py title="2025\day08\solution.py" ins="solve" ins="tuple[int, int]" ins=/for (i, \\()box1, box2(\\)) in (enumerate\\()pairs(, start=1\\))/ ins="part_1 =" ins={11,19-21,24-26,28-31,33}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        boxes: list[Box] = [
            tuple(map(int, line.split(","))) for line in self.input
        ]
        # Sort each pair by their Euclidean distance to each other
        pairs = sorted(combinations(boxes, 2), key=lambda pair: dist(*pair))

        part_1, part_2 = None, None
        uf = UnionFind(boxes)
        num_initial_pairs = 10 if self.testing else 1000

        # Make each connection from closest to farthest
        for i, (box1, box2) in enumerate(pairs, start=1):
            uf.union(box1, box2)

            # If all the initial connections have been made, get the
            # answer for Part 1
            if i == num_initial_pairs:
                part_1 = prod(sorted(uf.set_sizes, reverse=True)[:3])

            # If there is only one circuit, get the answer for Part 2
            if len(uf.set_sizes) == 1:
                part_2 = box1[0] * box2[0]

            if part_1 is not None and part_2 is not None:
                break
        else:
            assert False  # We will always get both answers

        return part_1, part_2
```

It seems that most of the complexity was front-loaded this time -- less so if
you knew about "union-find" beforehand (which I didn't). I quite like this data
structure, though; I'll have to keep it in mind if I ever need to deal with
disjoint sets -- and that _could_ be more often than you'd think!
