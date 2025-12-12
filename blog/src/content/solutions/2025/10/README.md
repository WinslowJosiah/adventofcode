---
year: 2025
day: 10
title: "Factory"
slug: 2025/day/10
pub_date: "2025-12-11"
# concepts: [recursion]
---
## Part 1

We're asked to press buttons to toggle some lights. This somewhat reminds of me
of the game [Lights Out](https://en.wikipedia.org/wiki/Lights_Out_(game)), which
is nice.[^lights-out]

[^lights-out]: I have fond memories of Lights Out. I never owned the physical
game, but well over a decade ago I coded not just [one](https://www.ticalc.org/archives/files/fileinfo/457/45751.html),
but [two](https://www.ticalc.org/archives/files/fileinfo/457/45769.html)
versions of it for my TI graphing calculator. Takes me back.

Input parsing is in order. All of the space-separated parts of each line -- the
indicator lights, the button wirings, and joltage requirements -- are enclosed
in some form of brackets, which we can remove before doing anything with them.
And [extended iterable unpacking](https://peps.python.org/pep-3132) is used to
store the middle parts (i.e. the raw button wirings) into a list.

```py title="2025\day10\solution.py"
from collections.abc import Sequence, Set

type Wiring = Set[int]

def parse_machine(line: str) -> tuple[Wiring, Sequence[Wiring], list[int]]:
    raw_indicators, *raw_buttons, raw_joltages = (
        part[1:-1] for part in line.split()
    )

    indicators = {i for i, ch in enumerate(raw_indicators) if ch == "#"}
    buttons = [
        set(map(int, raw_button.split(",")))
        for raw_button in raw_buttons
    ]
    joltages = list(map(int, raw_joltages.split(",")))
    return indicators, buttons, joltages
```

This is how I chose to represent each part of a factory machine:

1. The indicator lights are a `set` of the lights that are are on.
2. Each button is a `set` of the indicator lights it toggles.
3. The joltage requirements are a `list` of each target level.

The reason I chose to make indicator lights and buttons `set`s is because of the
[symmetric difference](https://docs.python.org/3/library/stdtypes.html#set.symmetric_difference)
(`^`) operator. The symmetric difference of two sets is all the elements in one
set or the other, but not both. So if you have a set `A`, getting its symmetric
difference with set `B` acts like a toggle; anything from `B` is removed from
`A` if it exists, and added to `A` if it doesn't. That sounds perfect for
toggling lights.

We can pretty easily try all different ways to press buttons to see if any of
them result in a specified indicator pattern. Because pressing a button twice
will toggle its connected lights twice (and thus have no effect), each button
would only need to be pressed once. So we can use [`itertools.combinations`](https://docs.python.org/3/library/itertools.html#itertools.combinations)
in a nested loop to test all possible button groups of all possible lengths,
returning once a button group leads to a matching pattern of indicator lights.

```py title="2025\day10\solution.py"
from itertools import combinations

type Presses = tuple[Wiring, ...]

def configure_indicators(
        indicators: Wiring,
        buttons: list[Wiring],
) -> int | None:
    for num_presses in range(len(buttons) + 1):
        for presses in combinations(buttons, num_presses):
            pattern: Wiring = set()
            for button in presses:
                pattern ^= button
            if pattern == indicators:
                return num_presses
    return None
```

We will tally up the total number of button presses over all machines to get our
result.

```py title="2025\day10\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        num_indicator_presses = 0
        for line in self.input:
            indicators, buttons, _ = parse_machine(line)

            indicator_result = configure_indicators(indicators, buttons)
            assert indicator_result is not None
            num_indicator_presses += indicator_result

        return num_indicator_presses
```

With that, Part 1 is done! But I'm always a little suspicious of puzzles that
tell us to ignore features of the input for Part 1... what's up with those
"joltage requirements"?

## Part 2

Turns out the joltage levels function as counters, and each button will
increment some of those counters. This had me somewhat worried; if Part 1
reminded me of Lights Out, Part 2 reminded me of [the linear algebra](https://www.youtube.com/watch?v=0fHkKcy0x_U)
you would need to do to systematically solve that game.

Many in [the Reddit solution thread](https://reddit.com/comments/1pity70) were
also reminded of linear algebra, and solved this puzzle with the linear algebra
capabilities of external libraries like [SciPy](https://scipy.org), [NumPy](https://numpy.org),
and [Z3](https://github.com/Z3Prover/z3). Some folks who didn't use external
libraries ended up writing [their own linear equation solver](https://github.com/Noble-Mushtak/Advent-of-Code/blob/main/2025/day10/solution2.py)
-- and initially, [so did I](https://github.com/WinslowJosiah/adventofcode/blob/dfa7da41095d2e70c1fc4c41ed3903ea23e6cd08/solutions/2025/day10/solution.py).

Some AoC puzzles require heavy use of algebra,[^aoc-algebra] and I was ready to
write this day's puzzle off as "the algebra puzzle" -- that is, until I saw
[an illuminating post](https://reddit.com/comments/1pk87hl) by `u/tenthmascot`
in the Advent of Code subreddit. In it, they presented a solution approach that
uses no linear algebra at all -- and in all honesty, I'm surprised I didn't
think of it myself.[^didnt-think-of-it-myself]

[^aoc-algebra]: For a good example of this, see [2023 Day 24](/solutions/2023/day/24).

[^didnt-think-of-it-myself]: I believe my mind was at least going in the right
direction. I noticed that pressing the same button twice increased the joltages
but did nothing to the indicator lights, so my first thought was to iterate
through all possible ways of matching the diagram of indicator lights and find
one that gives the right joltage levels.

    I had glossed over the part of the prompt that said to _ignore_ the
    indicator lights for Part 2... so that approach as-is would _never_ have
    worked. I suppose I was still gobsmacked from [Day 9](/solutions/2025/day/9)
    and not yet thinking clearly.

I'll be adapting their approach below. I would encourage you to read
[their original Reddit post](https://reddit.com/comments/1pk87hl) as well; the
approach is very well explained over there.

---

For this, I'll use a concrete example from the sample input (with the indicator
lights removed, because they don't matter).

```text
(3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
```

Once we've pressed the right buttons, the joltage levels should be `{3,5,4,7}`.
But let's imagine the machine was still connected to the indicator lights; if we
press those same buttons, what would they look like? Well, toggling a light an
even number of times does nothing, so _the only lights that would be on_ would
correspond to _the odd joltage levels_. In this case, `{3,5,4,7}` is {**odd**,
**odd**, **even**, **odd**}, so the indicator lights would look like `[##.#]`.

Crucially, _every_ way to reach joltage levels `{3,5,4,7}` will result in lights
`[##.#]`. So to reach those joltage levels, we can first reach that state of
indicator lights, and then do some even number of button presses[^including-zero]
afterwards to boost the joltages and leave the lights unchanged.

[^including-zero]: Including zero!

It'll be useful to precalculate the different indicator light patterns you can
get from button combinations. Let's change our `configure_indicators` function
to instead do this precalculation, and return the result in a `dict`.[^patterns-dict]

[^patterns-dict]: It's a `defaultdict`, but who's counting?

    Also, note that the keys are `frozenset`s instead of `set`s, because
    `frozenset`s are hashable.

```py title="2025\day10\solution.py" ins={1,5-9,17,19} ins="valid_patterns" ins=/(dict\\[Wiring, list\\[Presses\\]\\]):/ del={15-16,18}
from collections import defaultdict
...

def valid_patterns(buttons: Sequence[Wiring]) -> dict[Wiring, list[Presses]]:
    """
    Precompute all possible indicator patterns and the combinations of
    button presses that produce them.
    """
    patterns: dict[Wiring, list[Presses]] = defaultdict(list)
    for num_presses in range(len(buttons) + 1):
        for presses in combinations(buttons, num_presses):
            pattern: Wiring = set()
            for button in presses:
                pattern ^= button
            if pattern == indicators:
                return num_presses
            patterns[frozenset(pattern)].append(presses)
    return None
    return patterns
```

And to fix our now-broken Part 1 solution, we should make a new
`configure_indicators` function that instead uses our precalculated data.

```py title="2025\day10\solution.py" ins={1-6,15} ins=/, (patterns)/
def configure_indicators(
        indicators: Wiring,
        patterns: dict[Wiring, list[Presses]],
) -> int | None:
    presses_list = patterns.get(frozenset(indicators), [])
    return min((len(presses) for presses in presses_list), default=None)

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...
        for line in self.input:
            ...
            patterns = valid_patterns(buttons)

            indicator_result = configure_indicators(indicators, patterns)
            ...
        ...
```

Going back to our `{3,5,4,7}` example, what button combos will result in the
light pattern `##.#`? If we try printing our precalculated data for that
pattern, we get four ways to do it:

1. Pressing `(3)` and `(0,1)`.
2. Pressing `(1,3)`, `(2)`, and `(0,2)`.
3. Pressing `(2)`, `(2,3)`, and `(0,1)`,
4. Pressing `(3)`, `(1,3)`, `(2,3)`, and `(0,2)`.

Let's consider the first one: pressing `(3)` and `(0,1)`. After doing those
presses, the remaining joltage values will be `{2,4,4,6}` -- all even numbers,
because the state of the indicator lights is correct. And to leave the lights
unchanged, we need to reach our new target joltages in an even number of button
presses.

We can easily do that by finding the presses needed to reach _half_ of this
target, and doing those same presses _twice_. In this case, we would reach
`{2,4,4,6}` by figuring out how to reach `{1,2,2,3}` and doing those presses
twice.

Do you see what just happened? We've stated a solution to a _bigger_ problem in
terms of the solution to a _smaller_ problem. In other words... we've got a good
basis for a recursive solution. Let's spell out the recursive case and the base
case:

- **Recursive case**:
    1. Find the indicator light pattern we'd have after reaching the target
    joltage levels.
    2. For each button combo that results in that pattern, find all ways of
    reaching _half_ the remaining joltage values.
    3. One possible number of button presses would be the length of that initial
    combo plus two times the length of the combo reaching the half-target.
    4. The result will be the minimum of those button-press counts.
- **Base case**: If all joltage levels are 0, the minimum number of button
presses to reach those joltages will be 0.

```py title="2025\day10\solution.py"
from functools import cache

def configure_joltages(
        joltages: list[int],
        patterns: dict[Wiring, list[Presses]],
) -> int | None:
    # NOTE Pressing a button twice does nothing to the indicator lights,
    # but increases some joltages by 2. So we can configure the joltages
    # by first reaching the corresponding indicator state, then pressing
    # some other set of buttons twice to make up the difference.
    # Idea from u/tenthmascot: https://redd.it/1pk87hl
    @cache
    def get_min_presses(target: tuple[int, ...]) -> int | None:
        # No button presses are needed to reach zero joltage
        if not any(target):
            return 0

        # We must turn on the indicators with odd joltage levels
        indicators = frozenset(
            i for i, joltage in enumerate(target) if joltage % 2 == 1
        )
        result = None
        for presses in patterns[indicators]:
            # Simulate button presses to reach indicator state
            target_after = list(target)
            for button in presses:
                for joltage_index in button:
                    target_after[joltage_index] -= 1
            # Skip if any levels become negative
            if any(joltage < 0 for joltage in target_after):
                continue

            # All new target levels are even; calculate min presses to
            # reach half the target levels
            half_target = tuple(joltage // 2 for joltage in target_after)
            num_half_target_presses = get_min_presses(half_target)
            if num_half_target_presses is None:
                continue
            # We can reach the target by reaching the half-target twice;
            # add twice the half-target presses to the initial ones
            num_presses = len(presses) + 2 * num_half_target_presses

            # Update minimum presses count
            if result is None:
                result = num_presses
            else:
                result = min(result, num_presses)

        return result

    return get_min_presses(tuple(joltages))
```

The implementation above basically follows that description, but it also takes
the following points into account:

- If at any point we reach an impossible state -- e.g. a joltage target becomes
negative, or there's no way to reach the half-target -- whatever button presses
we're looking at won't help us reach the joltage targets, and we should skip
them.
- Because it may be the case that some joltage targets are impossible to reach,
we should return some default value in those cases. I used `None` because it's
the [obvious](https://pep20.org/#obvious) way to signify "no result".[^infinity]
- Plenty of recursive calls will be repeated, especially at the depeest levels
of recursion. Decorating our recursive function with [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache)
will improve the runtime.

[^infinity]: Sometimes, it may be preferable to return infinity -- or, in lieu
of that, some impractically large number. I decided against that in this case,
but it would've certainly saved us some special handling of `None` every time we
used `min`.

The hard part is over, and we can now add the result for each machine in a total
like in Part 1.

```py title="2025\day10\solution.py" ins="solve" ins="tuple[int, int]" ins=", num_joltage_presses" ins=", 0" ins={14-16}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        num_indicator_presses, num_joltage_presses = 0, 0
        for line in self.input:
            indicators, buttons, joltages = parse_machine(line)
            patterns = valid_patterns(buttons)

            indicator_result = configure_indicators(indicators, patterns)
            assert indicator_result is not None
            num_indicator_presses += indicator_result

            joltage_result = configure_joltages(joltages, patterns)
            assert joltage_result is not None
            num_joltage_presses += joltage_result
        return num_indicator_presses, num_joltage_presses
```

I have to admit, I was a bit bummed at first that the solution seemed to require
using/writing an equation solver (even if [my attempt at writing one](https://github.com/WinslowJosiah/adventofcode/blob/dfa7da41095d2e70c1fc4c41ed3903ea23e6cd08/solutions/2025/day10/solution.py)
was less painful than I imagined). But I'm glad I found someone that talked
about this recursive approach, because it's a much more elegant way to think of
the puzzle. I'll leave you with a quote from `u/tenthmascot`'s [original post](https://reddit.com/comments/1pk87hl):

> ...finding this solution genuinely redeemed the problem in my eyes: it went
> from "why does this problem exist?" to "_wow_." I hope it can do the same for
> you too.
>
> -- `u/tenthmascot`

It sure did.
