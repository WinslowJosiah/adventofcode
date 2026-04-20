---
year: 2024
day: 5
title: "Print Queue"
slug: 2024/day/5
pub_date: "2026-04-20"
# concepts: []
---
## Part 1

We're doing several printing jobs where certain page numbers must be printed
before others. The job of correctly ordering the pages to fit this requirement
is called [topological sorting](https://en.wikipedia.org/wiki/Topological_sorting).
But for now, we don't need to _do_ any topological sorting; we just want to
_check_ which lists of pages are topologically sorted.

First, let's parse the page ordering rules and the updates. The whole input is
in the form of two blocks separated by `\n\n` (my solution template allows me to
do this automatically, but you'll want to call `str.split` on your input
explicitly). Each of these blocks has multiple lines, which can be split with
`str.splitlines`.

```py title="2024\day05\solution.py"
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        raw_rules, raw_updates = (part.splitlines() for part in self.input)
        ...
```

The list of updates is a list of lists of integers, and is simple to parse.

For the page ordering rules, I decided to represent them as a `dict` mapping
each page to a `set` of its predecessors; for example, if `47|53` were a rule,
then `47 in predecessors[53]` would be true, because page 47 must go before
page 53. This way, checking whether any given rule exists involving two pages
can be done quickly.

```py title="2024\day05\solution.py"
from collections import defaultdict

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        # updates will hold updates as lists of page numbers
        updates = [
            [int(u) for u in raw_update.split(",")]
            for raw_update in raw_updates
        ]
        # predecessors will map pages to pages that must go before them
        predecessors: dict[int, set[int]] = defaultdict(set)
        for raw_rule in raw_rules:
            before, after = map(int, raw_rule.split("|"))
            predecessors[after].add(before)
        ...
```

We can then use this predecessor `dict` to make a function that checks whether a
given update follows the rules. An update follows the rules if and only if no
pair of pages is in an invalid order; in other words, if a page `before` comes
before a page `after` in the update, there can't be a rule that says `after`
must be a predecessor of `before`.

```py title="2024\day05\solution.py"
from itertools import combinations

def follows_rules(
        update: list[int], 
        predecessors: dict[int, set[int]],
) -> bool:
    return not any(
        after in predecessors[before]
        for before, after in combinations(update, 2)
    )
```

:::tip
This function uses [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
to get the pairs of `before` and `after` pages. As I also pointed out on [Day 2](/solutions/2024/day/2),
the items in each combination it returns will be in the _same order_ as they
were given, which is a useful feature to know about.
:::

And now, we can total the middle items of every update that follows the page
ordering rules!

```py title="2024\day05\solution.py" {3-4}
...

def middle_item(lst: list[int]) -> int:
    return lst[len(lst) // 2]

class Solution(StrSplitSolution):
    ...
    def part_1(self) -> int:
        ...
        total = 0
        for update in updates:
            if follows_rules(update, predecessors):
                total += middle_item(update)

        return total
```

(I also went ahead and created a `middle_item` function to grab the middle
element of the update, for ease of [readability](https://pep20.org/#readability).)

## Part 2

Now that the correctly ordered updates have been processed, we want to process
the _incorrectly_ ordered updates by ordering them correctly. In other words, we
must now do some topological sorting.

As Tim Peters wrote in [The Zen of Python](https://pep20.org), "there should be
one-- and preferably only one --obvious way to do it"[^tim-peters-toowtdi] --
though which way is most obvious can depend on how much you know about the
language and the relevant algorithms.

[^tim-peters-toowtdi]: This principle is a reference to the motto of the
programming language Perl, "there's more than one way to do it". The point seems
to be, while there _is_ more than one way to do it, it _should_ be obvious in
Python _which_ way to do something in a given scenario.

    Amusingly, the way Tim Peters expressed his principle is a bit
    tongue-in-cheek -- a ["joke"](https://github.com/python/cpython/issues/47614#issuecomment-1093430153),
    as he would later describe it. Em dashes are used three times in the Zen of
    Python, all with different conventions for the spacing around them -- none
    of which seem "obvious". That's one of many funny things about the Zen.

- In my [initial solution](https://github.com/WinslowJosiah/adventofcode/blob/02cb694657855a17ade48dc1229712aa95692bbb/aoc/2024/day05/__init__.py#L56-L65),
I used the fact that the input overspecified the order to write a single
`sorted` expression (even though how it works requires a bit of explanation).
- Those who knew a bit more about topological sorting used [Kahn's algorithm](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm),
a standard algorithm for topological sorting.
- And those who knew deeply about Python's standard library used [`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter),
a class made to assist in topological sorting. (In my opinion, _this_ is the
"obvious" solution.)[^topological-sorter]

[^topological-sorter]: For an example of a good solution that uses
`graphlib.TopologicalSorter`, see [this writeup](https://advent-of-code.xavd.id/writeups/2024/day/5/)
by David Brownman.

However, I saw one approach taken by a few people (including the ever-clever
[`u/4HbQ` on Reddit](https://www.reddit.com/r/adventofcode/comments/1h71eyz/comment/m0i09b0/))
which I found interesting, and which I probably would've used myself if I knew
about it back in 2024. So I'll be explaining that approach instead -- especially
because I will likely never have an excuse to explain it again.

---

Because this problem involves a type of "sorting", it would be nice if we could
directly use the `list.sort` method or `sorted` function in the solution. These
functions have a `key` parameter which can be used to sort by a custom rule, and
items are compared by calling that key function on them and comparing their
results.

In this scenario, we can't seem to directly apply a key function. Given two
pages, we can only figure out the relative order of those two pages. This is
more conducive to a [comparison function](https://docs.python.org/3/howto/sorting.html#comparison-functions),
which takes two items and returns a negative value for "less than", zero for
"equal", and a positive value for "greater than". (Comparison functions were the
_only_ way to sort by a custom rule before Python 2.4, and they're still
commonly used in low-level languages like C or C++.)

```py title="2024\day05\solution.py" ins="solve" ins="tuple[int, int]" ins={7-16}
...

class Solution(StrSplitSolution):
    ...
    def solve(self) -> tuple[int, int]:
        ...
        def cmp_pages(a: int, b: int) -> int:
            """Old-style comparison function for page numbers."""
            # If page A comes before page B, A goes first
            if a in predecessors[b]:
                return -1
            # If page B comes before page A, B goes first
            if b in predecessors[a]:
                return 1
            # Otherwise, it doesn't matter which page goes first
            return 0
        ...
```

Sometimes, this is the best you can do. And the team behind Python not only
recognizes this, but accommodates for it with [`functools.cmp_to_key`](https://docs.python.org/3/library/functools.html#functools.cmp_to_key).
This function allows a comparison function to be converted to a key function --
which, especially for cases like this, is occasionally useful.

For this solution, we can sort each update that doesn't follow the rules by
converting our custom `cmp_pages` comparison function to a key function. Then
it's only a matter of adding the middle pages of those sorted updates to a
separate total.

```py title="2024\day05\solution.py" ins={1,12-14} ins="part_1, part_2" ins=", 0"
from functools import cmp_to_key
...

class Solution(StrSplitSolution):
    ...
    def solve(self) -> tuple[int, int]:
        ...
        part_1, part_2 = 0, 0
        for update in updates:
            if follows_rules(update, predecessors):
                part_1 += middle_item(update)
            else:
                sorted_update = sorted(update, key=cmp_to_key(cmp_pages))
                part_2 += middle_item(sorted_update)

        return part_1, part_2
```

The thing I like most about this approach is the fact that you don't have to
know what topological sorting is, or how to do it, to come up with it. It's a
neat example of a clever use of the Python standard library.
