from collections.abc import Iterable


def aoc2023_day08_part1(lines: Iterable[str]) -> int:
    from itertools import cycle
    import re

    # This regex will match nodes, and group the source and destinations
    node_regex = re.compile(r"(\w{3}) = \((\w{3}), (\w{3})\)")

    def walk(
            src_node: str,
            nodes: dict[str, tuple[str, str]],
            turns: list[int],
    ) -> int:
        """
        Walk through a series of nodes until a destination node is
        reached.
        """
        steps = 0
        node = src_node
        for turn in cycle(turns):
            # If end node has been reached, stop walking
            if node == "ZZZ":
                return steps
            # Make next step
            node = nodes[node][turn]
            steps += 1

        assert False  # This makes the type checker happy

    line_iter = iter(lines)
    # First line is series of L/R characters
    turns = ["LR".index(c) for c in next(line_iter)]
    # Second line is blank
    next(line_iter)

    nodes: dict[str, tuple[str, str]] = {}
    # Collect info for all nodes
    for line in line_iter:
        # Get info for this node
        re_match = node_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        src, dest_L, dest_R = re_match.groups()
        # Add this node to the mapping of nodes
        nodes[src] = (dest_L, dest_R)

    # Walk through the nodes from the start node
    return walk("AAA", nodes, turns)


def aoc2023_day08_part2(lines: Iterable[str]) -> int:
    from itertools import cycle
    from math import lcm
    import re

    # This regex will match nodes, and group the source and destinations
    node_regex = re.compile(r"(\w{3}) = \((\w{3}), (\w{3})\)")

    def walk(
            src_node: str,
            nodes: dict[str, tuple[str, str]],
            turns: list[int],
    ) -> int:
        """
        Walk through a series of nodes until a destination node is
        reached.
        """
        steps = 0
        node = src_node
        for turn in cycle(turns):
            # If end node has been reached, stop walking
            if node.endswith("Z"):
                return steps
            # Make next step
            node = nodes[node][turn]
            steps += 1

        assert False  # This makes the type checker happy

    line_iter = iter(lines)
    # First line is series of L/R characters
    turns = ["LR".index(c) for c in next(line_iter)]
    # Second line is blank
    next(line_iter)

    nodes: dict[str, tuple[str, str]] = {}
    # Collect info for all nodes
    for line in line_iter:
        # Get info for this node
        re_match = node_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        src, dest_L, dest_R = re_match.groups()
        # Add this node to the mapping of nodes
        nodes[src] = (dest_L, dest_R)

    # NOTE: To find an efficient solution, we need to make some crucial
    # assumptions about the input data:
    # 1. Walking from any source node will lead to a unique
    # destination node.
    # 2. Walking from any destination node will lead to the same
    # destination node, and no other destination node in between.
    # 3. The path from each source node to its destination node is the
    # same length as the path from the destination node to itself.
    # This means each path effectively acts as an oscillator of a fixed
    # length, and the question can be reduced to finding the LCM (lowest
    # common multiple) of the path lengths.

    # Walk through the nodes from the start nodes, then get the LCM of
    # their path lengths
    return lcm(*[
        walk(node, nodes, turns)
        for node in nodes
        if node.endswith("A")
    ])


parts = (aoc2023_day08_part1, aoc2023_day08_part2)
