---
year: 2023
day: 19
title: "Aplenty"
slug: 2023/day/19
pub_date: "2025-11-06"
# concepts: [regex, higher-order-functions]
---
## Part 1

Holy cow, this one is gonna be complex. But you know what they say:
[complex is better than complicated](https://pep20.org/#complex). Let's try to
break this down into simpler tasks.

1. We need to parse the data into a more convenient format.
    - A part can be a `dict` -- in fact, they look almost like `dict`s already!
    - A workflow would preferably be a function that takes a part and returns
    which workflow to send it to. We could make a function that returns such a
    function -- in other words, a [higher-order function](https://en.wikipedia.org/wiki/Higher-order_function).
2. We need to write a function which takes a part, sends it through the proper
workflows until it's **A**ccepted or **R**ejected, and adds up all of its
ratings.
3. We need to take each part, run it through the `in` workflow, and add up the
resulting ratings.
    - A generator expression inside a `sum` will do the trick.

First, let's do the parsing.

Parsing the parts will be easy. Each of the `xmas` ratings is in the form
`x=123`, so we can use a simple regex to find them all; from there, it becomes a
simple `dict` comprehension.

```py title="2023\day19\solution.py"
import re

type Part = dict[str, int]

def parse_part(raw_part: str) -> Part:
    return {k: int(v) for k, v in re.findall(r"(.)=(\d+)", raw_part)}
```

We can use a regex to parse the workflows as well. We can retrieve the capturing
groups from a `re.Match` object using the [`groups`](https://docs.python.org/3/library/re.html#re.Match.groups)
property. Before writing our `parse_workflow` function, let's test out our
regex:

```py
>>> import re
>>> raw_workflow = "px{a<2006:qkq,m>2090:A,rfg}"
>>> re.search(r"(.*){(.*)}", raw_workflow)
<re.Match object; span=(0, 27), match='px{a<2006:qkq,m>2090:A,rfg}'>
>>> _.groups()
('px', 'a<2006:qkq,m>2090:A,rfg')
```

What we're left with is the name of the workflow, and a comma-separated string
of filtering rules (ending with the default destination for when no filters
apply). We'll use this info to build the workflow, but first we should write a
function to parse those filters.

```py title="2023\day19\solution.py"
from collections.abc import Callable
from operator import gt, lt

def parse_filter(
        raw_filter: str
) -> tuple[str, Callable[[int, int], bool], int, str]:
    """
    Parse filter string, and return its category, operator function,
    value, and destination.
    """
    category = raw_filter[0]
    op = gt if raw_filter[1] == ">" else lt
    value_str, destination = raw_filter[2:].split(":")
    return category, op, int(value_str), destination
```

This is mostly simple. Note, however, that we return the `>` or `<` operator not
as a character, but as a _function_ (imported from the [`operator`](https://docs.python.org/3/library/operator.html)
module),[^technically-higher-order] so we can call it while running the
workflow.

[^technically-higher-order]: That technically makes `parse_filter` a
higher-order function, because it's a function that returns a function. But the
`parse_filter` function does only _part_ of the job.

We'll need to use the filtering rules and default destination in order to run
the workflow. Running the workflow involves checking the given part against each
filtering rule, and returning the rule's destination if it matches that rule --
or the default destination if no rules matched.

For example, the rule `a<2006:qkq` means we check if the part's `a` rating is
less than 2006, and if it is, its destination is `qkq`. We can call the operator
function returned by `parse_filter` to check for whether each filtering rule is
matched.

```py title="2023\day19\solution.py"
type Filter = Callable[[Part], str]

def build_workflow(raw_filters: str, default: str) -> Filter:
    """
    Create a function that applies filters to a `Part` and returns its
    destination if any (and `default` otherwise).
    """
    def _apply_filters(part: Part) -> str:
        for raw_filter in raw_filters.split(","):
            if not raw_filter:
                continue
            category, op, value, destination = parse_filter(raw_filter)
            if op(part[category], value):
                return destination
        return default

    return _apply_filters
```

And like I mentioned before, this `build_workflow` function returns the actual
workflow-running function, so we can call it on any part we want to run through
the workflow.

Now we can create a `parse_workflow` function that puts it all together. It'll
return the name of the workflow and the workflow-running function built from the
rest of the information.

```py title="2023\day19\solution.py"
def parse_workflow(raw_workflow: str) -> tuple[str, Filter]:
    if not (match := re.search(r"(.*){(.*)}", raw_workflow)):
        raise ValueError(f"could not parse workflow: {raw_workflow}")
    name, raw_filters = match.groups()
    raw_filters, default = raw_filters.rsplit(",", maxsplit=1)
    return name, build_workflow(raw_filters, default)
```

Returning both the name and workflow function is convenient, because we can use
the `dict()` constructor to build a `dict` mapping workflow names to functions.

```py title="2023\day19\solution.py"
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        workflows_block, parts_block = self.input
        workflows: dict[str, Filter] = dict(
            parse_workflow(line)
            for line in workflows_block.splitlines()
        )
        ...
```

---

Second, let's write the part-scoring function.

What we want it to do is send the part through a given workflow, which may send
it to a different workflow, etc. until the part is **A**ccepted (and its score
is the sum of its ratings) or **R**ejected (and its score is 0).

While recursion might not be the first way you think of to implement this, it
turns out to be simple to implement if you think of it this way.

- **Base case**: If the "workflow name" is `R`, the part is rejected and its
score is 0. If the "workflow name" is `A`, the part is accepted and its score is
the sum of its ratings.
- **Recursive case**: Once we send the part through the given workflow, we will
get a destination workflow (which is either `A` or `R` -- in which case, we're
basically done -- or another named workflow). The part's score will be whatever
its score is after being sent to that destination workflow.

```py title="2023\day19\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...
        def score_part(workflow_name: str, part: Part) -> int:
            if workflow_name == "R":
                return 0
            if workflow_name == "A":
                return sum(part.values())
            return score_part(workflows[workflow_name](part), part)
        ...
```

Perhaps this could have been done with an iterative approach -- i.e. iterating
until the "workflow name" was `A` or `R` -- but I like the [sparseness](https://pep20.org/#sparse)
of the recursive approach.

---

Lastly, let's write the final `sum` expression for our answer.

All we need to do is score each part upon passing it to the `in` workflow.

```py title="2023\day19\solution.py"
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...
        return sum(
            score_part("in", parse_part(line))
            for line in parts_block.splitlines()
        )
```

There were lots of steps that we needed to be careful about, but now we have our
answer.

## Part 2

This one will also require tons of care.

Instead of testing specific parts, we want to know how many would be accepted if
we tested _every possible part_. But brute-forcing all 256 trillion possible
parts isn't going to be feasible.

So instead, we should probably think about the `xmas` ratings not as numbers,
but as _ranges_ of numbers; each time a filtering rule is applied, these ranges
will shrink as they are passed around to each workflow. Let's call this
part-like thing with ranges of ratings a `RangedPart` -- a `dict` mapping the
categories from `xmas` to `range`s, in the same way regular `Part`s map
categories to `int`s.

We'll need to create a function based on `build_workflow` to handle these
`RangedPart`s. As the ranges shrink, different groups of parts will be sent to
different workflows, so the function will instead return a list of destination
workflows and the `RangedPart`s that reach them.

```py title="2023\day19\solution.py" ins={1-2,7,16} del={4,15}
type RangedPart = dict[str, range]
type RangedFilter = Callable[[RangedPart], list[tuple[str, RangedPart]]]

def build_workflow(raw_filters: str, default: str) -> Filter:
def build_ranged_workflow(raw_filters: str, default: str) -> RangedFilter:
    def _apply_filters(part: RangedPart):
        ranges: list[tuple[str, RangedPart]] = []

        for raw_filter in raw_filters.split(","):
            if not raw_filter:
                continue
            category, op, value, destination = parse_filter(raw_filter)
            ...  # TODO Add apply-next-filter code

        return default
        return ranges

    return _apply_filters
```

Now, what exactly happens to the ranges as the filtering rules are applied? They
get split into two ranges: one that fits the rule, and one that doesn't. We can
create a function that splits a range along a given value; the first range will
go up _to_ that value (exclusive), and the second range will go up _from_ that
value (inclusive).

```py title="2023\day19\solution.py"
def split_range(r: range, value: int) -> tuple[range, range]:
    return range(r.start, value), range(value, r.stop)
```

Then, as each `RangedPart` is sent through the workflow, we split the ranges
according to the rule, send the matching portion of the range to the
corresponding destination, and update the `RangedPart` with the non-matching
portion. The results are appended to the `ranges` list as we go along.

Note that we need to be a little careful with how we split the ranges to avoid
an off-by-one error:

- If the operator is `>`, the matching portion starts at _the number after_ the
filter's value (because we want numbers that are greater than that value).
- If the operator is `<`, the matching portion ends at the filter's value
(because `range` objects are exclusive at the stopping value).

```py title="2023\day19\solution.py" ins={12-18,20} ins=" + [(default, part)]"
def build_ranged_workflow(raw_filters: str, default: str) -> RangedFilter:
    """
    Create a function that applies filters to a `RangedPart` and returns
    a list of destinations and the `RangedPart`s that reach them.
    """
    def _apply_filters(part: RangedPart) -> list[tuple[str, RangedPart]]:
        ranges: list[tuple[str, RangedPart]] = []
        for raw_filter in raw_filters.split(","):
            if not raw_filter:
                continue
            category, op, value, destination = parse_filter(raw_filter)
            if op == gt:
                unsent, sent = split_range(part[category], value + 1)
            else:
                sent, unsent = split_range(part[category], value)

            ranges.append((destination, {**part, category: sent}))
            part = {**part, category: unsent}

        # The RangedPart that matched no filters gets sent to `default`
        return ranges + [(default, part)]

    return _apply_filters
```

:::tip
One short way to create a copy of a `dict` with some values changed is by using
dictionary unpacking with `**`. It works similarly to iterable unpacking with
`*`, except it works with key-value pairs in a mapping.

```py
>>> part = {k: range(1, 4001) for k in "xmas"}
>>> {**part, "a": range(1, 2006)}
{'x': range(1, 4001),
 'm': range(1, 4001),
 'a': range(1, 2006),
 's': range(1, 4001)}
>>> {**part, "m": range(2091, 4001)}
{'x': range(1, 4001),
 'm': range(2091, 4001),
 'a': range(1, 4001),
 's': range(1, 4001)}
```

Here, `**part` fills the new `dict` with the key-value pairs from `part`, and
the key-value pairs defined afterwards will update the filled values.
:::

Now that we have two different workflow-builder functions, we should make that
configurable in `parse_workflow`.

```py title="2023\day19\solution.py" ins="[F]" ins=/str, (F)/ ins=/key, (builder)/ ins={3}
def parse_workflow[F](
        raw_workflow: str,
        builder: Callable[[str, str], F],
) -> tuple[str, F]:
    if not (match := re.search(r"(.*){(.*)}", raw_workflow)):
        raise ValueError(f"could not parse workflow: {raw_workflow}")
    key, raw_filters = match.groups()
    raw_filters, default = raw_filters.rsplit(",", maxsplit=1)
    return key, builder(raw_filters, default)
```

:::note
The return types of the workflow-builder functions aren't compatible with each
other, but I want the `builder` argument to correctly type-check for both of
them. To ensure that, I'm making `parse_workflow` a [generic function](https://typing.python.org/en/latest/spec/generics.html)
-- a function that uses a generic type variable, which can stand in for
basically any type.

The specific syntax I'm using for it was added in Python 3.12. Before that, I'd
have to annotate that function like this:

```py {1,3} /, (F)/
from typing import TypeVar

F = TypeVar("F")

def parse_workflow(
    raw_workflow: str,
    builder: Callable[[str, str], F],
) -> tuple[str, F]
    ...
```

Of course, this (and every other type annotation I write) is only needed for
static type checking, which is entirely optional. I like writing correct type
annotations in my code, though, and my code editor agrees.
:::

This will allow us to pass either function to `parse_workflow`, depending on
whether we're in Part 1 or Part 2, and it will build the proper type of
workflow.

```py title="2023\day19\solution.py" ins=", build_workflow" ins=", build_ranged_workflow"
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        workflows_block, parts_block = self.input
        workflows = dict(
            parse_workflow(workflow_line, build_workflow)
            for workflow_line in workflows_block.splitlines()
        )
        ...

    def part_2(self) -> int:
        workflows_block, _ = self.input
        workflows = dict(
            parse_workflow(workflow_line, build_ranged_workflow)
            for workflow_line in workflows_block.splitlines()
        )
        ...
```

Now for the final piece of the solution: we have to use our `RangedPart`s and
"ranged workflows" to tally up the parts that would be accepted. We can do this
similarly to how we were doing it before, using a recursive function.

- **Base case**: If the "workflow name" is `R`, _none_ of the parts are
accepted. If the "workflow name" is `A`, any part where each `xmas` rating is
within the given ranges is accepted, so the number of accepted parts is the
product of the lengths of the ranges.
- **Recursive case**: Once we send the `RangedPart` through the given workflow,
we will get several `RangedPart`s and destination workflows in return. To get
the number of accepted parts, we can tally the number of accepted parts when
sending each `RangedPart` to its destination workflow, and sum the results.

Using a dictionary comprehension, we will initialize each range in the
`RangedPart` to `range(1, 4001)` (meaning, each category could have the full
range of values from 1 to 4,000); we will then send this `RangedPart` to the
`in` workflow.

```py title="2023\day19\solution.py"
from math import prod
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...
        def score_workflow(workflow_name: str, part: RangedPart) -> int:
            if workflow_name == "R":
                return 0
            if workflow_name == "A":
                return prod(len(r) for r in part.values())
            return sum(
                score_workflow(next_key, next_part)
                for next_key, next_part in workflows[workflow_name](part)
            )

        return score_workflow("in", {k: range(1, 4001) for k in "xmas"})
```

Phew, this was a long one. But we made it out alive with solutions to both
parts!
