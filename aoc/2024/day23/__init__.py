from collections.abc import Iterable, Iterator, Mapping


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
    import itertools as it

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


def find_maximal_cliques[N](
        graph: Mapping[N, Iterable[N]],
        clique: set[N] | None = None,
        potential_nodes: set[N] | None = None,
        excluded_nodes: set[N] | None = None,
) -> Iterator[set[N]]:
    """
    Find all maximal cliques (cliques that cannot be extended by adding
    another node) in a graph.

    This function uses the Bron-Kerbosch algorithm with pivoting.
    """
    if clique is None:
        clique = set()
    if potential_nodes is None:
        potential_nodes = set(graph.keys())
    if excluded_nodes is None:
        excluded_nodes = set()

    # Yield this clique if it's maximal (no nodes could be added to it)
    if not potential_nodes and not excluded_nodes:
        yield clique
        return

    # NOTE We can choose a "pivot" node, and only explore its
    # non-neighbors as potential nodes to add to the clique. We will
    # still find all maximal cliques this way; otherwise, if only
    # neighbors of the pivot were in the maximal clique, we could add
    # the pivot to it, which contradicts its maximality.
    pivot = (potential_nodes | excluded_nodes).pop()

    # For each node that could be added to the clique
    for node in potential_nodes - set(graph[pivot]):
        neighbors = set(graph[node])
        # Find all cliques that also include this node
        yield from find_maximal_cliques(
            graph,
            clique=clique | {node},
            potential_nodes=potential_nodes & neighbors,
            excluded_nodes=excluded_nodes & neighbors,
        )
        # Don't add this node to future cliques
        potential_nodes.remove(node)
        excluded_nodes.add(node)


def aoc2024_day23_part2(lines: Iterable[str]) -> str:
    computers = get_computers(lines)
    cliques = find_maximal_cliques(computers)
    # Get the maximum clique, sorted alphabetically
    # NOTE A "maximum clique" is a maximal clique with the largest size.
    return ",".join(sorted(max(cliques, key=len)))


parts = (aoc2024_day23_part1, aoc2024_day23_part2)
