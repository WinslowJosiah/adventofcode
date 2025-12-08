# https://adventofcode.com/2025/day/8

from collections.abc import Iterable
from itertools import combinations
from math import dist, prod

from ...base import StrSplitSolution, answer


type Box = tuple[int, ...]


# REVIEW Do I want this to go in a utility module? Maybe, but we'll see.
class UnionFind[T]:
    """
    A disjoint set ("union-find") data structure.

    Disjoint sets are stored in the form of a forest of trees. The root
    of each tree is the "representative" of that set; two items with the
    same representative are in the same set. This allows for efficient
    `union` and `find` operations in nearly O(1) amortized time.
    """

    def __init__(self, items: Iterable[T]):
        """
        Create a new union-find structure with each item in its own set.

        Parameters
        ----------
        items : iterable
            The items to be stored in the union-find structure.
        """
        items_list = list(items)
        # NOTE An item is "its own parent" if and only if it is a root.
        self.parent = {item: item for item in items_list}
        # Track the size of each tree at its root
        self.size = {item: 1 for item in items_list}

    def find(self, item: T) -> T:
        """
        Find the "representative" (root of the corresponding tree) of
        the set containing `item`.

        Path compression is used to flatten the structure of the tree,
        which makes future `find` operations faster.

        Parameters
        ----------
        item : item
            The item to find the representative for.

        Returns
        -------
        item
            The representative of the set containing `item`.
        """
        # Compress the path to the root
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        # Now the item's "parent" will be the root of its set
        return self.parent[item]

    def union(self, item1: T, item2: T):
        """
        Merge the sets containing `item1` and `item2`.

        Parameters
        ----------
        item1 : item
            An item from the first set.
        item2 : item
            An item from the second set.
        """
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
        # root2 is no longer a root, so it shouldn't store have a size
        del self.size[root2]

    @property
    def set_sizes(self) -> list[int]:
        """
        Get the sizes of all sets. They are returned in an arbitrary
        order.

        Returns
        -------
        list of int
            The sizes of all sets.
        """
        return list(self.size.values())


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 8.
    """
    _year = 2025
    _day = 8

    @answer((164475, 169521198))
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
