---
year: 2023
day: 8
title: "Haunted Wasteland"
slug: 2023/day/8
pub_date: "2025-10-17"
# concepts: []
---
## Part 1

First order of business: input parsing.

- Once the string of left/right turns is extracted, [`itertools.cycle`](https://docs.python.org/3/library/itertools.html#itertools.cycle)
is a perfect way to repeat the sequence of turns for as long as needed.
- To build the network of nodes, we can extract the source, left, and right node
of each connection with a simple regex, and store all the connections in a
`dict`.

```py title="2023\day08\solution.py"
from itertools import cycle
import re

class Solution(StrSplitSolution):
    separator = "\n\n"

    def _parse_input(self) -> tuple[cycle[str], dict[str, dict[str, str]]]:
        raw_turns, raw_nodes = self.input
        turns = cycle(raw_turns)
        nodes: dict[str, dict[str, str]] = {}
        for line in raw_nodes.splitlines():
            root, l, r = re.findall(r"\w+", line)
            nodes[root] = {"L": l, "R": r}
        return turns, nodes
```

Our Part 1 solution can now be just a simple loop, starting at node `AAA`,
walking through the network, and ending at node `ZZZ`. The loop also needs to
keep track of the number of steps taken, so we'll use `enumerate` to loop
through the cycle of turns.

```py title="2023\day08\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        turns, nodes = self._parse_input()
        current = "AAA"
        for turn_index, turn in enumerate(turns):
            if current == "ZZZ":
                return turn_index
            current = nodes[current][turn]
        # NOTE The loop is infinite unless the path ends, so this is
        # never reached. But the type checker doesn't know that.
        assert False
```

I like the fact that we were able to use `itertools.cycle`; the `itertools`
module is full of neat iteration methods like that.

## Part 2

The very first thing I thought of was doing multiple network walks at once
starting with every node ending in `A`, and brute-forcing until every walk
reached a node ending in `Z`. But that isn't going to finish in a reasonable
timeframe.

Back when I was first solving this, I had no idea what else to do. This was the
first day where I looked up other people's solutions _before_ writing my own.

As I would later find out, this is in a genre of puzzle which forces you to
notice some non-trivial features of the puzzle input.[^not-in-sample-input] I'll
illustrate those features with the following function, which takes a starting
node and prints which ending nodes are reached and when:

[^not-in-sample-input]: Which are _not_ in the sample input, by the way. So
you'd never know just from reading the prompt.

```py title="2023\day08\solution.py" ins={8,11,13-15} "_debug_walks" ", current: str"
...

class Solution(StrSplitSolution):
    ...

    def _debug_walks(self, current: str):
        turns, nodes = self._parse_input()
        print(f"start node = {current}")
        for turn_index, turn in enumerate(turns):
            if current.endswith("Z"):
                print(f"  found end node {current} at turn {turn_index}")
            current = nodes[current][turn]
            # After some time, we get the point
            if turn_index > 100_000:
                return
```

Here's the output I get for all nodes ending in `A` (it will be different for
your input):

```text
start node = DRA
  found end node HMZ at turn 20777
  found end node HMZ at turn 41554
  found end node HMZ at turn 62331
  found end node HMZ at turn 83108
start node = AAA
  found end node ZZZ at turn 18673
  found end node ZZZ at turn 37346
  found end node ZZZ at turn 56019
  found end node ZZZ at turn 74692
  found end node ZZZ at turn 93365
start node = CMA
  found end node RNZ at turn 13939
  found end node RNZ at turn 27878
  found end node RNZ at turn 41817
  found end node RNZ at turn 55756
  found end node RNZ at turn 69695
  found end node RNZ at turn 83634
  found end node RNZ at turn 97573
start node = MNA
  found end node XKZ at turn 17621
  found end node XKZ at turn 35242
  found end node XKZ at turn 52863
  found end node XKZ at turn 70484
  found end node XKZ at turn 88105
start node = NJA
  found end node LFZ at turn 19199
  found end node LFZ at turn 38398
  found end node LFZ at turn 57597
  found end node LFZ at turn 76796
  found end node LFZ at turn 95995
start node = RVA
  found end node DDZ at turn 12361
  found end node DDZ at turn 24722
  found end node DDZ at turn 37083
  found end node DDZ at turn 49444
  found end node DDZ at turn 61805
  found end node DDZ at turn 74166
  found end node DDZ at turn 86527
  found end node DDZ at turn 98888
```

Two key things to notice here:

1. Each starting node goes to a unique ending node.
2. The walk ends up _looping_, taking the same number of steps every time to
reach that ending node.

So to find the point at which every walk reaches its ending node at the same
time, we just need to find the lengths of each of these loops; the point at
which they sync up is their :abbr[LCM]{title="least common multiple"}, which we
can use [`math.lcm`](https://docs.python.org/3/library/math.html#math.lcm) to
calculate.

```py title="2023\day08\solution.py" ins={1,16,19-24} ins=/def (_solve)/
from math import lcm
...

class Solution(StrSplitSolution):
    def _solve(self, current: str) -> int:
        turns, nodes = self._parse_input()
        for turn_index, turn in enumerate(turns):
            if current.endswith("Z"):
                return turn_index
            current = nodes[current][turn]
        # NOTE The loop is infinite unless the path ends, so this is
        # never reached. But the type checker doesn't know that.
        assert False

    def part_1(self) -> int:
        return self._solve("AAA")

    def part_2(self) -> int:
        _, nodes = self._parse_input()
        # NOTE Each start node acts like a fixed-length oscillator with
        # its unique destination node; the point at which all
        # destination nodes are reached simultaneously is the LCM of all
        # the path lengths.
        return lcm(*[self._solve(n) for n in nodes if n.endswith("A")])
```

Not too bad, but I'm not the biggest fan of this genre of puzzle. I don't like
[having to guess](https://pep20.org/#ambiguity) at unspecified features,
especially if they don't apply to the sample input.
