from collections.abc import Iterable
import itertools as it


def get_computers(lines: Iterable[str]) -> dict[str, set[str]]:
    """
    Parse a list of connections between computers, and return a mapping
    between computers and the other computers connected with them.
    """
    computers: dict[str, set[str]] = {}
    for line in lines:
        name_a, name_b = line.split("-")
        computers.setdefault(name_a, set()).add(name_b)
        computers.setdefault(name_b, set()).add(name_a)
    return computers


def aoc2024_day23_part1(lines: Iterable[str]) -> int:
    computers = get_computers(lines)
    groups: set[frozenset[str]] = set()
    for name, connections in computers.items():
        # At least one computer must have a name starting with a T
        if not name.startswith("t"):
            continue
        # The other computers must be connected with the first one...
        for conn_a, conn_b in it.combinations(connections, 2):
            # ...and connected with each other
            if conn_a in computers[conn_b]:
                groups.add(frozenset([name, conn_a, conn_b]))

    return len(groups)


def aoc2024_day23_part2(lines: Iterable[str]) -> str:
    computers = get_computers(lines)
    groups: set[frozenset[str]] = set()
    seen: set[frozenset[str]] = set()
    for name_a, connections_a in computers.items():
        for name_b in connections_a:
            # Start with two computers that are connected
            group = {name_a, name_b}
            # Skip if we've already made a group starting with these two
            # computers
            if frozenset(group) in seen:
                continue
            seen.add(frozenset(group))

            # The other computers in the group must be connected with
            # both of the first computers
            group_connections = connections_a & computers[name_b]
            # While there are computers left to process
            while group_connections:
                conn = group_connections.pop()
                if conn in group:
                    continue
                # If this computer is connected to every other computer
                # in the group
                if all(conn in computers[cpu] for cpu in group):
                    # It belongs in the group
                    group.add(conn)
                    # The computers it's connected to might belong in
                    # the group
                    group_connections.update(computers[conn])
            groups.add(frozenset(group))

    # Get the largest group by length, sorted alphabetically
    return ",".join(sorted(max(groups, key=len)))


parts = (aoc2024_day23_part1, aoc2024_day23_part2)
