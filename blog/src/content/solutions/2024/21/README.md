---
year: 2024
day: 21
title: "Keypad Conundrum"
slug: 2024/day/21
pub_date: "2026-11-23"
# concepts: [recursion]
---
## Part 1

I've heard of long and complicated passwords, but _this_ is ridiculous. This day
seems like it'll be very confusing, but I promise it's manageable; try your best
to bear with me.

We have a complex series of robots controlling two kinds of keypads: numeric and
directional. You, the human keypad operator, will be controlling a _directional_
keypad; this will control a series of robots on _directional_ keypads, which
will ultimately control a robot on a _numeric_ keypad. And for each of five
numeric codes you must enter, you must calculate its "complexity" by multiplying
the following values:

- The _length of the shortest button sequence_ you can type on your directional
keypad to ultimately cause the code to be typed on the numeric keypad.
- The _numeric part of the code_, excluding the `A` at the end.

Clearly, the first of these values will be the harder one to calculate and think
about, so I want to tackle it first. For clarity, let's call it the **cost** of
the code.

In fact, it'll be useful to look at this puzzle with different numbers of
robots, which will result in different costs for the same code. So when I talk
about a code's "**cost with $n$ robots**", I mean the length of the shortest
button sequence you can use to cause that code to be entered into the final
keypad, _when there are $n$ robots between you and the final keypad_.

This time, I think it'll help to first solve a simpler version of this
cost-finding problem manually; this is a good technique to gain an understanding
of a big problem that seems intractable.

### Manual example

For this example, the code I'll be using is _extremely_ simple: the single digit
`2`. We'll attempt to find the cost of this simple code with different numbers
of robots between us and the numeric keypad: **zero** robots, **one** robot,
**two** robots, and finally **three** robots. As we do this, keep in mind that
the point of this exercise is not to find the answers _per se_; rather, the
point is to discover the necessary _techniques_, so we can use them in the full
program.

#### Cost with zero robots

If there are zero robots between us and the numeric keypad -- in other words, if
_we're_ controlling the keypad -- what's the shortest way we can type the code
`2`? The answer is obvious: just press the `2` button. This means that the cost
of our numeric code with zero robots is **1**, because we're pressing only one
button.

:::note
In general, this means that the cost of _any_ code with zero robots involved
will be the _length_ of that code; for example, the cost of `029A` with zero
robots would instead be 4.
:::

#### Cost with one robot

```text
+---+---+---+
| 7 | 8 | 9 |
+---+---+---+
| 4 | 5 | 6 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
    | 0 | A |
    +---+---+
```

Now we're going to add a robot -- which, for sake of clarity, we'll call
**Advent**. Advent the robot will be placed on the `A` button of the numeric
keypad, and we will control Advent with a _directional_ keypad. We want to make
Advent move to the `2` button and then press it; our answer will be the length
of the shortest directional button sequence we can use to do this.

It may seem obvious how to walk Advent from `A` to `2`... though to prepare us
for walking a robot between _any_ two buttons, it's worth thinking in detail
about which ways of doing so are worth it to consider. Let's lay down some
ground rules.

- Because we want to use the shortest button sequence, we must take the shortest
path between two buttons. No doubling back (e.g. `><` or `v^`), no going in a
loop (e.g. `>^<v`)... simply go left/right just enough to get to the correct
column, and go up/down just enough to get to the correct row.
    - For example, if we wanted to walk Advent from `A` to `8`, we'd need
    exactly one `<` press and three `^` presses.
- Once we know how many left/right presses and up/down presses we need, we only
have to consider up to _two_ ways to order these presses: the one with all
_horizontal_ presses first, and the one with all _vertical_ presses first. From
here, we keep only the _valid_ button sequences, i.e. the ones that don't lead
the robot to walk over a gap.
    - For example, if we wanted to walk Advent from `A` to `7`, we'd need two
    `<` presses and three `^` presses -- meaning we'd only consider `<<^^^` and
    `^^^<<`. But since `<<^^^` crosses the gap, `^^^<<` would be the only valid
    sequence to keep.

:::note
You might be wondering: what's the purpose of that second ground rule? Why
wouldn't we consider sequences that alternate between buttons, like `^<^<^`?

Let's say we chose to use a sequence like that, and then we added one more robot
between us and the numeric keypad. Now that robot has to perform that `^<^<^`
sequence... and _we_ have to make that robot move to the `^` button, then all
the way to the `<` button, then all the way back to `^`, then back to `<`, then
back to `^`... which seems like a waste of movement.

It's _much_ less costly for us to walk the robot to one button, have it press
that button repeatedly, and then walk it to the other button. This is what the
second ground rule is for: keeping the cost low in the long run.
:::

Sometimes, following these rules will narrow down our robot-walking button
sequences to _one_ valid choice. But most of the time, they'll leave us with
_two_ possible button sequences -- which, until we know how they affect the
robots above us, we can't yet narrow down. That's okay; we just have to keep
track of these branching families of button sequences for as long as we can.

In this case, we're left with _two_ ways to get Advent to enter a `2`:

1. Press `<^` to make Advent go from `A` to `2`, and press `A` to make Advent
press `2`.
2. Press `^<` to make Advent go from `A` to `2`, and press `A` to make Advent
press `2`.

This means the two possible Advent-controlling sequences are `<^A` and `^<A`,
and so the cost of our numeric code with one robot is **3**. Let's keep both of
these sequences in mind for the next case.

#### Cost with two robots

```text
    +---+---+
    | ^ | A |
+---+---+---+
| < | v | > |
+---+---+---+
```

Now we introduce a different robot -- let's call it **Blizzard**. Like Advent,
Blizzard the robot will start on the `A` button... but _not_ on the numeric
keypad. Blizzard will take our place on the directional keypad we were just
using to control Advent, and we'll instead be controlling Blizzard using our own
directional keypad. This time, we want Blizzard to enter _either_ `<^A` or
`^<A`, so that Advent is controlled to enter the numeric code we ultimately
want.

Let's focus on only the `<^A` code for now. We know from the previous step how
to make a robot press a _single_ button, so how do we extend that to make a
robot press _multiple_ buttons? We can simply have the robot follow this
press-a-single-button process multiple times, and then string all the actions
together. For example, to enter `<^A`, Blizzard would need to:

1. Move from `A` to `<`, and press the button.
2. Move from `<` to `^`, and press the button.
3. Move from `^` to `A`, and press the button.

Keeping our ground rules in mind for how to walk a robot between buttons, here
are the ways we would do these steps.

1. To make Blizzard press `<`:
    - Blizzard must move from `A` to `<`.
    - The two button sequences for us to consider are `<<v` and `v<<`.
    - `<<v` would walk Blizzard over the gap in the directional keypad, so that
    sequence is invalid.
    - Thus, we should use `v<<` to walk Blizzard to the button, and `A` to make
    Blizzard press it.
2. To make Blizzard press `^`:
    - Blizzard must move from `<` to `^`.
    - The two button sequences for us to consider are `>^` and `^>`.
    - `^>` would walk Blizzard over the gap in the directional keypad, so that
    sequence is invalid.
    - Thus, we should use `>^` to walk Blizzard to the button, and `A` to make
    Blizzard press it.
3. To make Blizzard press `A`:
    - Blizzard must move from `^` to `A`.
    - Because we don't have any vertical presses in our sequence, the only
    button sequence for us to consider is `>`.
    - Thus, we should use `>` to walk Blizzard to the button, and `A` to make
    Blizzard press it.

We happen to have a single choice for how to do each step, leading to the single
sequence `v<<A>^A>A`. This causes Blizzard to enter `<^A`, which causes Advent
to enter `2` like we want. The length of our sequence is 9.

What about the _other_ code we could make Blizzard enter, `^<A`? When we do a
similar analysis on _this_ code,[^exercise-to-the-reader] it leads to _another_
single sequence: `<Av<A>>^A`. This causes Blizzard to enter `^<A`, which will
also cause Advent to enter `2` like we want. The length of _this_ sequence of
ours is also 9.

[^exercise-to-the-reader]: I'll leave this analysis as an exercise to the
reader. If you're looking to understand this process better, now's your chance
to try it out for yourself!

Since both of our possible Blizzard-controlling sequences have a length of 9,
the cost of our numeric code with two robots ends up being **9**. Let's again
keep both of these sequences in mind for our last step.

#### Cost with three robots

Finally, we introduce yet another robot -- let's call it **Carol**. Carol the
robot, like Advent and Blizzard before it, starts on the `A` button of the
keypad we just used. Carol will now control Blizzard, and we will now control
Carol on our own directional keypad. And this time, we want Carol to enter
either of the 9-length sequences (`v<<A>^A>A` or `<Av<A>>^A`) we found in the
previous step, to make Blizzard do what we want it to do, and eventually to make
Advent enter the numeric code we want.

First, what is our cost if we want Carol to enter `v<<A>^A>A`? We can do the
same button-by-button analysis as before, and get a series of valid shortest
button sequences we could use to get Carol to press each button in its code. The
resulting sequences are summarized below; the total cost in this case turns out
to be 21.

| Step           | Sequence(s)    | Step Cost | Total Cost |
| -------------- | -------------- | --------- | ---------- |
| `A` &rarr; `v` | `<vA` or `v<A` | 3         | 3          |
| `v` &rarr; `<` | `<A`           | 2         | 5          |
| `<` &rarr; `<` | `A`            | 1         | 6          |
| `<` &rarr; `A` | `>>^A`         | 4         | 10         |
| `A` &rarr; `>` | `vA`           | 2         | 12         |
| `>` &rarr; `^` | `<^A` or `^<A` | 3         | 15         |
| `^` &rarr; `A` | `>A`           | 2         | 17         |
| `A` &rarr; `>` | `vA`           | 2         | 19         |
| `>` &rarr; `A` | `^A`           | 2         | **21**     |

Just to be sure, though, let's do the analysis for the _other_ sequence we could
have Carol enter: `<Av<A>>^A`. This time, when we do our button-by-button
breakdown, we find that the total cost would be _25_... which is interesting.

| Step           | Sequence(s)    | Step Cost | Total Cost |
| -------------- | -------------- | --------- | ---------- |
| `A` &rarr; `<` | `v<<A`         | 4         | 4          |
| `<` &rarr; `A` | `>>^A`         | 4         | 8          |
| `A` &rarr; `v` | `<vA` or `v<A` | 3         | 11         |
| `v` &rarr; `<` | `<A`           | 2         | 13         |
| `<` &rarr; `A` | `>>^A`         | 4         | 17         |
| `A` &rarr; `>` | `vA`           | 2         | 19         |
| `>` &rarr; `>` | `A`            | 1         | 20         |
| `>` &rarr; `^` | `<^A` or `^<A` | 3         | 23         |
| `^` &rarr; `A` | `>A`           | 2         | **25**     |

Both of the Blizzard-controlling sequences we want Carol to perform have the
_same_ cost, and the _same_ ultimate effect on Advent... and yet, the resulting
Carol-controlling sequences have _different_ costs! Up until this point, all
sequences we've derived at each level have had the same costs as each other, and
it didn't matter which one we used; _this_ shows us that, even if two different
sequences have the same cost with one amount of robots, their costs may diverge
by the time more robots get involved.

Now we know why it was worth it at each level to keep track of multiple
same-cost sequences: by the time we had to find Carol-controlling sequences,
they evolved into two separate families of sequences, one of length 21 and one
of length 25. The smaller of these two lengths is 21, so the cost of our numeric
code with three robots is **21**.

### Approach

After stepping through the manual example, which features of our solution
process can we pull from to come up with a programmatic solution approach? Even
with a general idea of what's going on, being able to define a specific approach
based on that can be difficult. But at least for me, here's how it all coalesced
into the approach I used.

The most important observation, which I was able to gleam from the start, is
that this puzzle has a _recursive_ structure to it; the structure of robots is
self-similar, with each robot along the line solving a smaller version of the
complete setup. What we enter into our keypad depends on what Carol is supposed
to enter, which depends on what Blizzard is supposed to enter, and so on down
the line. This means the function which calculates the cost of a code -- which
I call `cost` -- will need to be recursive, and the recursion should be based on
the number of robots between us and the final keypad which the code will be
entered into -- the numeric keypad for the full puzzle, or one of the
directional keypads above it for the intermediate steps.

And here's a second observation it took me a while to realize how to use
effectively: a button sequence is made up of many individual button presses. For
a given number of robots between us and a keypad, the cost of a button press on
that keypad only depends on where its robot _starts_ and _ends_, and the best
way to walk between each pair of buttons can be chosen independently. This means
that we can express the cost of a button sequence with $n$ robots as the sum of
the costs of each individual button press with $n$ robots. For this reason, I
ended up turning this "cost-of-one-press" operation into its own function, which
I call `cost_between` -- i.e. the cost of walking a robot between two buttons
and then pressing `A`.

Let's define how `cost` will work. It will take a code, a keypad the code will
be entered into, and the number of robots between us and that keypad. It will be
a recursive function, with a **base case** and a **recursive case**.

- **Base case**: If there are zero robots between us and the final keypad (i.e.
if _we're_ controlling the final keypad), the cost of the code is its _length_.
- **Recursive case**: If there are $n$ robots between us and the final keypad,
the robot on that keypad must move to each button in the code and press it --
first from `A` to the first button, then from the first button to the second,
then from the second to the third, etc. We will use `cost_between` to calculate
the cost of pressing each button with $n$ robots; the cost of the code is the
sum of all of these one-button costs.

Note that the recursive case of `cost` doesn't directly call `cost`, but instead
it calls `cost_between`... so what makes `cost` a recursive function? Well,
because `cost_between` will involve calculating the cost of some other codes,
`cost_between` will call `cost`. This is an indirect form of recursion called
[mutual recursion](https://en.wikipedia.org/wiki/Mutual_recursion), where two or
more functions are defined in terms of each other.

With that said, let's define how `cost_between` will work. It will take a
starting button, an ending button, a keypad the ending button will be pressed
on, and the number of robots between us and that keypad.

- First, find all paths from the starting button to the ending button which fit
our ground rules (i.e. using exactly as many `^`/`v`/`<`/`>` presses as
necessary, ordered horizontal-first or vertical-first, and _not_ moving the
robot over a gap in the keypad).
- Append an `A` press to each path, and find the costs of the resulting
sequences with _one fewer_ robot. We will use `cost` to calculate these costs.
- The answer will be the lowest of these costs.

Now that the long walk of understanding and specifying our approach is over,
we're finally ready to start implementing. Are you still with me? I hope you
are, because I don't know how to simplify it _any_ further than this.

### Implementation

We _finally_ get to write some Python!

First, to get it out of the way, I'll present the way I represented the keypads:
as `tuple`s of `str` rows of buttons, with each character representing a button
and a `_` character representing a gap. We'll want to know the row and column of
a button if we ask for it, so I also wrote a small `find_button` function to
return just that.

```py title="2024\day21\solution.py"
type Keypad = tuple[str, ...]
NUMERIC_KEYPAD: Keypad = ("789", "456", "123", "_0A")
DIRECTIONAL_KEYPAD: Keypad = ("_^A", "<v>")
GAP = "_"

def find_button(button: str, keypad: Keypad) -> tuple[int, int]:
    for r, row in enumerate(keypad):
        for c, char in enumerate(row):
            if char == button:
                return (r, c)
    raise RuntimeError(f"button {button} not found")
```

In the ["Approach"](#approach) section, I discussed how the `cost` and
`cost_between` functions we need to write will work. Those will indeed be the
most important functions in this solution. But before we get to implementing
them, I'll write some functions that they depend on, which I'll call `walk` and
`paths_between`.

`walk` is a [generator](https://docs.python.org/3/howto/functional.html#generators)
function that basically simulates the act of walking a robot on a keypad from
one location to another. It takes a starting row/column on the keypad, the
keypad itself, and a path for the robot to walk on it (using `^`/`v`/`<`/`>` as
directions). At each step the robot takes, a lookup table is used to change the
robot's location based on the direction it's going. And after each step, the
function `yield`s the keypad button the robot lands on.

```py title="2024\day21\solution.py" ins={1}
from collections.abc import Iterator

OFFSETS = {">": (0, 1), "<": (0, -1), "v": (1, 0), "^": (-1, 0)}

def walk(row: int, col: int, keypad: Keypad, path: str) -> Iterator[str]:
    for direction in path:
        dr, dc = OFFSETS[direction]
        row += dr
        col += dc
        yield keypad[row][col]
```

And `paths_between` is a function that returns all paths between two buttons on
a keypad that are worth considering. It takes a starting button on the keypad,
an ending button on the keypad, and the keypad itself.

This path-finding is what we repeatedly ended up doing throughout the
["Manual example"](#manual-example) section. In fact, I use the same ground
rules I specified in the [one-robot example](#cost-with-one-robot): the path
must have exactly as many horizontal/vertical presses as needed, either
horizontal-first or vertical-first. And once both possible paths are created, we
want to return only the ones that don't cross over a gap, which we can check by
calling `walk` and checking that the gap character is not in the resulting
sequence.

```py title="2024\day21\solution.py"
def paths_between(start: str, end: str, keypad: Keypad) -> list[str]:
    start_row, start_col = find_button(start, keypad)
    end_row, end_col = find_button(end, keypad)

    dr, dc = end_row - start_row, end_col - start_col
    horizontal = ">" * dc + "<" * -dc
    vertical = "v" * dr + "^" * -dr
    # NOTE Any path worth taking will consist of a horizontal section
    # and a vertical section; anything else would cause robots to move
    # unnecessarily. So we will build those two sections of the path
    # with exactly as many presses as needed, and try both orderings.
    paths = [horizontal + vertical, vertical + horizontal]

    return [
        path
        for path in paths
        if GAP not in walk(start_row, start_col, keypad, path)
    ]
```

:::tip
One basic [operation you can do with sequences](https://docs.python.org/3/builtins/stdtypes.html#common-sequence-operations)
is multiplying them by an integer, which has the effect of repeating the
sequence that many times; for instance, `[4, 2] * 3` results in
`[4, 2, 4, 2, 4, 2]`. This is why expressions like `">" * dc` work to repeat a
string a certain number of times.

Interestingly, in the case of multiplying a sequence by a _negative_ number, it
is treated as multiplying by 0; for instance, `[4, 2] * -3` results in `[]` (the
empty list). This is similar to what would happen if you ran a `for` loop that
should technically have a negative number of iterations: it is completely
skipped and no iterations happen.

I use both of these operations when setting `horizontal` and `vertical`, to
repeat `">"` and `"v"` if the corresponding numbers are positive, and `"<"` and
`"^"` if they are negative.
:::

Now to implement `cost`. For as much preamble as I gave to ensure that how it
works is understood, the implementation itself is _extremely_ simple, only a few
lines long.

- If the given number of robots is 0 (i.e. the keypad is human-operated), we hit
the base case: the code's cost is its length.
- Otherwise, we get the cost by adding up the results of calling `cost_between`
for each pair of buttons the robot on the keypad must move between.
    - We prepend the code with `"A"` because the robot starts on the `A` button,
    and we can use [`itertools.pairwise`](https://docs.python.org/3/library/itertools.html)
    to iterate through all adjacent pairs of buttons. Then the answer can be
    translated to a straightforward `sum` expression.

```py title="2024\day21\solution.py" ins={1}
from itertools import pairwise

def cost(code: str, keypad: Keypad, num_robots: int) -> int:
    # If this is a human-operated keypad, the cost of any code is the
    # code's length; we can just press each button in turn
    if num_robots <= 0:
        return len(code)
    # Otherwise, the cost of this code is the total cost between all
    # pairs of buttons (starting with A, the robot's starting point)
    return sum(
        cost_between(start, end, keypad, num_robots)
        for start, end in pairwise("A" + code)
    )
```

And now to implement `cost_between`. Again, this will be an _extremely_ simple
function, a single expression depending on `cost` and `paths_between`. Each code
we want to test will be a path from `paths_between` followed by an `A` press; we
want the minimum cost of any of these codes on a directional keypad with one
fewer robot than we started with. (This translates pretty much directly to the
expression below.)

```py title="2024\day21\solution.py"
def cost_between(start: str, end: str, keypad: Keypad, num_robots: int) -> int:
    # The cost between these two buttons is the lowest cost that the
    # next-higher-up controller can achieve for any robot path
    return min(
        # NOTE The next-higher-up controller presses A at the end, to
        # make the robot press the end button.
        cost(path + "A", DIRECTIONAL_KEYPAD, num_robots - 1)
        for path in paths_between(start, end, keypad)
    )
```

Not so complicated after all, huh? At this point, I'm reminded of a quote from
Vi Hart's excellent video ["How I Feel About Logarithms"](https://vimeo.com/147902562):

> Sometimes to make the harder things simple, first you have to make the simple
> things harder.
>
> -- Vi Hart

This is what I have set out to do for this problem, and I hope I succeeded.

---

All of the necessary scaffolding is out of the way, so we can fill in the rest
of the solution quite smoothly.

Let's take a moment to remember the structure of the puzzle: we have _one_ robot
on a numeric keypad (which we want to enter our codes into), and _two_ robots on
directional keypads, meaning there are **three** robots between us and the final
keypad along the line. This means that our answer will involve finding the cost
of our codes on the numeric keypad with 3 robots.

Let's also remember why we wanted the cost of each code in the first place: so
that we can calculate the _complexity_ of each code. Now that `cost` has been
implemented, this is easy; the complexity of a code is its cost on the numeric
keypad with three robots, times its numeric part (without the final `A`
character) converted to an `int`.

```py title="2024\day21\solution.py"
def complexity(code: str) -> int:
    return cost(code, NUMERIC_KEYPAD, num_robots=3) * int(code[:-1])
```

Our answer will then be the `sum` of the `complexity` of each code from each
line of our puzzle input. (My solution framework allows me to automatically
split the input into lines; you'll want to use `str.split` or `str.splitlines`
to do the same.)

```py title="2024\day21\solution.py"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(complexity(code) for code in self.input)
```

_Phew_. We made it out alive.

## Part 2

Have you ever had to change your password, and then the new password is forced
to be even _more_ long and complicated than the old one? This is about a
_hundred million_ times worse.

Not to worry, though: our Part 1 solution cleanly generalizes to _any_ number of
robots. To make our `complexity` function generalized, we can just add a
`num_robots` parameter and pass it along in the calculation.

```py title="2024\day21\solution.py" ins=", num_robots: int" ins=/(num_robots)\\)/
def complexity(code: str, num_robots: int) -> int:
    return cost(code, NUMERIC_KEYPAD, num_robots=num_robots) * int(code[:-1])
```

This time, we have one robot on a numeric keypad, and _twenty-five_ robots on
directional keypads, making **twenty-six** robots in all between us and the
numeric keypad. Our Part 2 solution is _almost_ as easy as passing the number 26
instead of the number 3...

```py title="2024\day21\solution.py" ins=", num_robots=3" ins=", num_robots=26"
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(complexity(code, num_robots=3) for code in self.input)

    def part_2(self) -> int:
        return sum(complexity(code, num_robots=26) for code in self.input)
```

...except for the unfortunate fact that it takes too long to finish. _So_
close...

When a recursive approach like this takes too long to finish, it's probably
repeating a bunch of simple calculations that it doesn't have to. A simple way
to address this in Python is with [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache).
As I briefly mentioned on [Day 19](/solutions/2024/day/19), `functools.cache` is
a [decorator](https://docs.python.org/3/glossary.html#term-decorator) you can
apply to a function to _cache_ its outputs -- so that, if you give it the same
input, it will remember the output it gave back the first time and _reuse_ it,
saving the time it would take to recalculate that output. (You'd be surprised
how much time that can take, even for the _simplest_ functions!)

In this case, a good candidate for the `functools.cache` decorator is the
`cost_between` function, because finding the cost of moving a robot between two
buttons is slow enough and common enough that simply _remembering_ the results
will save us plenty of time. Once this decorator is imported, we can apply it to
`cost_between` by simply writing `@cache` above it.

```py title="2024\day21\solution.py" ins={1,3}
from functools import cache

@cache
def cost_between(start: str, end: str, keypad: Keypad, num_robots: int) -> int:
    ...  # Same code as before
```

This is indeed enough for us to get an answer extremely quickly -- in about 1.7
milliseconds on my machine! Once again, _phew_.
