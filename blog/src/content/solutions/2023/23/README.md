---
year: 2023
day: 23
title: "A Long Walk"
slug: 2023/day/23
pub_date: "2025-11-19"
# concepts: []
---
## Part 1

Another day, another grid puzzle. We'll be doing some pathfinding today... but
this time, we want the _longest_ distance from the start to the end.

First, let's parse the grid using our ever-useful [`grids` module](https://github.com/WinslowJosiah/adventofcode/tree/main/solutions/utils/grids.py),
ignoring all the `#` characters so they won't be in the grid. The starting tile
will be the earliest tile on the top row, and the the ending tile will be the
latest tile on the bottom row.

```py title="2023\day23\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        start, end = min(grid.keys()), max(grid.keys())
        ...
```

Now let's write a function that gets all valid moves starting from some point in
our grid. If we are starting on a slope, the only valid move is to follow it;
otherwise all four neighbors are valid moves (provided they're still in the
grid, of course).

```py title="2023\day23\solution.py"
SLOPES = {
    ">": Direction.RIGHT,
    "v": Direction.DOWN,
    "<": Direction.LEFT,
    "^": Direction.UP,
}

def get_moves_from(grid: Grid[str], point: GridPoint) -> list[GridPoint]:
    # If there is a slope here
    if slope := SLOPES.get(grid[point]):
        # Move along the slope
        moves = [add_points(point, slope.offset)]
    else:
        # Otherwise, move in all directions
        moves = list(neighbors(point, num_directions=4))

    return [m for m in moves if m in grid]
```

The problem we're being asked to solve -- the ["longest path problem"](https://en.wikipedia.org/wiki/Longest_path_problem)
-- is known to _not_ have an efficient algorithm to solve it in general.[^longest-path-problem-dag]
But even though we can't do much to speed up the search, we _can_ make the
search space a bit smaller. Most of the grid consists of long hallways with only
one path forward, so we can precalculate the distances along each of those
hallways so we end up with way fewer nodes to search through.

[^longest-path-problem-dag]: An efficient algorithm _is_ known for
[directed acyclic graphs](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
(:abbr[DAGs]{title="directed acyclic graphs"}) -- and for Part 1, our input
happens to be a :abbr[DAG]{title="directed acyclic graph"}. But such an
algorithm doesn't extend to Part 2, so I don't bother implementing it here.

This will give us a [graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics))
where the nodes are the intersections (and the start/end points), and the edges
that connect them store the distances along the hallways between them. Here's
what this should look like for the sample input:

```py
{(0, 1): {(5, 3): 15},
 (3, 11): {(11, 21): 30, (13, 13): 24},
 (5, 3): {(3, 11): 22, (13, 5): 22},
 (11, 21): {(19, 19): 10},
 (13, 5): {(13, 13): 12, (19, 13): 38},
 (13, 13): {(11, 21): 18, (19, 13): 10},
 (19, 13): {(19, 19): 10},
 (19, 19): {(22, 21): 5}}
```

This is a `dict` that maps each intersection to another intersection and the
distance to it (which will save us a lot of walking). For example:

- To walk from `(0, 1)` to `(5, 3)`, it takes `15` steps.
- To walk from `(3, 11)` to `(11, 21)`, it takes `30` steps.
- To walk from `(3, 11)` to `(13, 5)`, it takes `24` steps.
- To walk from `(5, 3)` to `(3, 11)`, it takes `22` steps.
- To walk from `(5, 3)` to `(13, 5)`, it takes `22` steps.
- etc.

Let's make a function that creates this graph. We'll be moving outwards from
each intersection until we reach another intersection, so first we should find
where the intersections _are_.

For our purposes, an intersection is any point with more than 2 valid moves from
it. In other words, you must be able to get into it one way, and get out of it
in more than one way. (We also include the start and end points manually, so we
also record paths starting and ending from there.)

```py title="2023\day23\solution.py"
from collections import defaultdict

type Graph = dict[GridPoint, dict[GridPoint, int]]

def create_graph(grid: Grid[str], start: GridPoint, end: GridPoint) -> Graph:
    # Gather all "intersections" (including the start and end nodes)
    intersections = {start, end} | {
        point
        for point in grid
        if len(get_moves_from(grid, point)) > 2
    }
    ...
```

The way we build the graphs is by considering all initial moves from all the
intersections we found, and continually moving forward from there until another
intersection is reached. If we ever run out of moves at any point in our current
path, we've hit a dead end and we should quit; otherwise, we record the distance
between the intersections in the graph.

```py title="2023\day23\solution.py"
def create_graph(grid: Grid[str], start: GridPoint, end: GridPoint) -> Graph:
    ...
    graph: Graph = defaultdict(dict)
    for intersection in intersections:
        for initial_move in get_moves_from(grid, intersection):
            if initial_move not in grid:
                continue

            # Start at this intersection; move in the initial direction
            previous, current = intersection, initial_move
            distance = 1
            while current not in intersections:
                # Get moves from here without doubling back
                moves = [
                    m
                    for m in get_moves_from(grid, current)
                    if m != previous
                ]
                # If there are no moves, we've hit a dead end
                if not moves:
                    break
                # NOTE The paths between intersections should be long
                # "hallways" with one path forward.
                assert len(moves) == 1, f"unexpected intersection at {current}"

                previous, current = current, moves[0]
                distance += 1
            else:
                # If we haven't hit a dead end, record the distance
                graph[intersection][current] = distance

    return graph
```

:::tip
On [Day 5](/solutions/2023/day/5) this year, I showcased the
[optional `else` clause](https://docs.python.org/3/tutorial/controlflow.html#else-clauses-on-loops)
on the `for` loop. This also applies to the `while` loop; the `else` clause will
run only if no `break` occurs.

Without the `while`..`else` clause, the code might look something like this:

```py {1,6,9-10}
dead_end_was_hit = False
while current not in intersection:
    ...
    # If there are no moves, we've hit a dead end
    if not moves:
        dead_end_was_hit = True
        break
    ...
if dead_end_was_hit:
    pass
else:
    # If we haven't hit a dead end, record the distance
    graph[intersection][current] = distance
```

However, not using an extra flag variable makes the code [more simple](https://pep20.org/#simple).
:::

We now need to find the longest path through this graph from the start to the
end. Here, I implement a basic recursive version of depth-first search (:abbr[DFS]{title="depth-first search"})
-- we search through all possible paths, and we update a `max_distance` variable
whenever we find a longer path. Note that as we go deeper into the search, we
add the current node to a set of `seen` nodes, and remove it once we're done;
this is how we keep track of nodes that are on the current path -- which we have
to do, because the path isn't allowed to double back on itself.

```py title="2023\day23\solution.py"
def find_longest_path(
        graph: Graph,
        start: GridPoint,
        end: GridPoint,
) -> int:
    max_distance = 0
    seen: set[GridPoint] = set()

    def search(node: GridPoint, distance: int):
        nonlocal max_distance
        if node == end:
            max_distance = max(max_distance, distance)
            return

        seen.add(node)
        for neighbor, distance_to_neighbor in graph[node].items():
            if neighbor not in seen:
                search(neighbor, distance + distance_to_neighbor)
        seen.remove(node)

    search(start, 0)
    return max_distance
```

:::attention
I declared `max_distance` as `nonlocal` in the inner function, which lets me
reassign what `max_distance` is in the outer function. If `nonlocal` wasn't
there, the inner function would only be able to reassign to a different
`max_distance` that lives within itself.

Note that I don't need to declare `seen` as `nonlocal`; that's because the inner
function doesn't _reassign_ to it, but simply _accesses_ it and calls its
methods. Here, the inner function doesn't find `seen` within itself, so it uses
`seen` from the outer function.
:::

At last, it's time to take our long walk. We will call the functions we made to
create the graph and find the longest path in it.

```py title="2023\day23\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        graph = create_graph(grid, start, end)
        return find_longest_path(graph, start, end)
```

Luckily, the naive :abbr[DFS]{title="depth-first search"} approach doesn't seem
to take _too_ long here -- only ~30.9 milliseconds on my machine. And I don't
have any other ideas for a general longest-path algorithm, so let's hope we can
just apply this to Part 2 without it being unreasonably slow.

## Part 2

Good news and bad news.

- Good news: we _can_ apply our Part 1 solution to Part 2 with minimal code
changes.
- Bad news: it just _barely_ runs at a reasonable speed. By which I mean, it
takes ~10.3 seconds to run on my machine -- about 330 times _slower_, and by far
the slowest solution this year.

As far as I know, there's very little we can do about that.[^meet-in-the-middle]
So let's just get modifyin'.

[^meet-in-the-middle]: I saw one slightly faster approach for Part 2 that took a
"meet-in-the-middle" approach -- a search would be conducted in _both_
directions, which would create full paths wherever the two searches met.

    Implementing this myself only saved me ~4 seconds on my machine, though --
    and it was extremely [complicated](https://pep20.org/#complex) and finnicky
    to get right -- so I didn't end up using that approach.

The only difference between Parts 1 and 2 is whether slopes are followed. So
once we pull out the main logic to a separate `_solve` function, we can pass
this as an argument to it, which we pass to `create_graph`...

```py title="2023\day23\solution.py" ins=/def (_solve)/ ins=", with_slopes: bool" ins=", with_slopes=with_slopes" ins={11-12,14-15}
...

class Solution(StrSplitSolution):
    def _solve(self, with_slopes: bool) -> int:
        grid = parse_grid(self.input, ignore_chars="#")
        start, end = min(grid.keys()), max(grid.keys())

        graph = create_graph(grid, start, end, with_slopes=with_slopes)
        return find_longest_path(graph, start, end)

    def part_1(self) -> int:
        return self._solve(with_slopes=True)

    def part_2(self) -> int:
        return self._solve(with_slopes=False)
```

...and which `create_graph` passes to `get_moves_from`...

```py title="2023\day23\solution.py" ins={5} ins=", with_slopes"
def create_graph(
    grid: Grid[str],
    start: GridPoint,
    end: GridPoint,
    with_slopes: bool,
) -> Graph:
    # Gather all "intersections" (including the start and end nodes)
    intersections = {start, end} | {
        point
        for point in grid
        if len(get_moves_from(grid, point, with_slopes)) > 2
    }

    graph: Graph = defaultdict(dict)
    for intersection in intersections:
        for initial_move in get_moves_from(grid, intersection, with_slopes):
            ...
            while current not in intersections:
                # Get moves from here without doubling back
                moves = [
                    m
                    for m in get_moves_from(grid, current, with_slopes)
                    if m != previous
                ]
                ...
    ...
```

...and which `get_moves_from` handles by only following the slope if our
`with_slopes` argument is true.

```py title="2023\day23\solution.py" ins={4} ins="we are following slopes and " ins="with_slopes and (" ins=/(\\)):/
def get_moves_from(
        grid: Grid[str],
        point: GridPoint,
        with_slopes: bool,
) -> list[GridPoint]:
    # If we are following slopes and there is a slope here
    if with_slopes and (slope := SLOPES.get(grid[point])):
        # Move along the slope
        moves = [add_points(point, slope.offset)]
    else:
        # Otherwise, move in all directions
        moves = list(neighbors(point, num_directions=4))

    return [m for m in moves if m in grid]
```

I'm a bit disappointed that there apparently isn't a lot I can do to speed up
Part 2... but hey, sometimes a puzzle is just computationally _hard_.
