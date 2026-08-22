---
year: 2024
day: 17
title: "Chronospatial Computer"
slug: 2024/day/17
pub_date: "2026-08-22"
# concepts: [recursion]
---
## Part 1

Instead of creating a program, we'll be creating the _computer_ it's running on.
Or at least, an [_emulator_](https://en.wikipedia.org/wiki/Emulator) for the
computer it's running on. Believe it or not, this task is nowhere near as scary
as it sounds.

First, let's parse the input. Today, it's in the form of two blocks separated by
two newlines: the initial values of the computer's registers, and the program
itself. Once you split the input into those two blocks (which I can configure my
solution framework to do for me), all we want are the _numbers_ from each block;
we can use a relatively simple one-liner to extract them.

```py title="2024\day17\solution.py"
import re

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> str:
        registers, program = (
            tuple(map(int, re.findall(r"\d+", block)))
            for block in self.input
        )
        ...
```

Now we have the register values and program values, both as `tuple`s of `int`s.
Once our emulator for the Historians' computer is finished, it'll need this
information to run the program.

Let's start work on our emulator, which will be in the form of a function.
Because the computer will be outputting a number of successive values as it runs
the program, a [generator](https://docs.python.org/3/howto/functional.html#generators)
function that `yield`s those output values seems like a good fit.

```py title="2024\day17\solution.py"
from collections.abc import Iterator

def run(registers: tuple[int, ...], program: tuple[int, ...]) -> Iterator[int]:
    a, b, c = registers
    ...  # TODO Write emulate-Historians'-computer code
```

Our emulation function will consist of one main loop, where the following things
will happen:

1. An instruction pointer (which starts at 0) will read an "opcode" and an
"operand".
2. Based on the opcode, one of eight different instructions will be performed.
3. The instruction pointer will increase by 2, and this process will loop until
the instruction pointer moves past the end of the program.

This is already enough to create a simple sketch of the function. We can use
some slick slicing syntax to read the current `opcode` and `operand`, and we can
use a [`match` statement](https://docs.python.org/3/tutorial/controlflow.html#match-statements)
to do different things based on the opcode we find (rather than a large,
unwieldy `if...elif` chain).

And while we're at it: some instructions will need a "combo operand" based on
the value of `operand`, so let's also figure out the value of the current
`combo` operand. Because we're only considering integer values of `operand` from
0 to 6, a tiny [lookup table](https://en.wikipedia.org/wiki/Lookup_table) is all
we need here.

```py title="2024\day17\solution.py" ins={6-31}
from collections.abc import Iterator

def run(registers: tuple[int, ...], program: tuple[int, ...]) -> Iterator[int]:
    a, b, c = registers

    pointer = 0
    while pointer < len(program):
        opcode, operand = program[pointer : pointer + 2]
        combo = [0, 1, 2, 3, a, b, c][operand]

        match opcode:
            case 0:  # adv (A DiVide)
                ...
            case 1:  # bxl (B Xor Literal)
                ...
            case 2:  # bst (B STore)
                ...
            case 3:  # jnz (Jump if Not Zero)
                ...
            case 4:  # bxc (B Xor C)
                ...
            case 5:  # out (OUTput)
                ...
            case 6:  # bdv (B DiVide)
                ...
            case 7:  # cdv (C DiVide)
                ...
            case _:
                assert False, f"unexpected opcode {opcode}"

        pointer += 2
```

All that's left is to implement the instructions for each opcode. And
thankfully, the puzzle prompt tells us the _exact_ behavior of each instruction,
so the implementations are very straightforward -- though it may help to
familiarize yourself with [bitwise operations](https://en.wikipedia.org/wiki/Bitwise_operation),
and how to use the [bitwise operators in Python](https://wiki.python.org/moin/BitwiseOperators).

0. `adv`: Integer-divide `a` by `pow(2, combo)`, and store the result back to
`a`.
    - I actually implement this slightly differently than described;
    integer-dividing by 2 (or a power of 2) is equivalent to a rightward
    [bit shift](https://en.wikipedia.org/wiki/Bitwise_operation#Bit_shifts),
    which we can do with the `>>` operator. So my implementation of `adv` is
    `a >>= combo` -- that is, take `a`, bit-shift it by `combo` bits to the
    right, and store the result back to `a`.
1. `bxl`: Do a [bitwise XOR](https://en.wikipedia.org/wiki/Bitwise_operation#XOR)
with `b` and `operand`, and store the result back to `b`.
    - Python's bitwise XOR operator is `^`, so `bxl` can be implemented as
    `b ^= operand`.
2. `bst`: Calculate `combo` modulo 8 (which keeps only its lowest 3 bits), and
store the result to `b`.
    - I also implement this slightly differently than described -- not with the
    modulo operator `%`, but with the [bitwise AND](https://en.wikipedia.org/wiki/Bitwise_operation#AND)
    operator `&`. It [may not be obvious](https://pep20.org/#dutch) why I did it
    that way, but a bitwise AND is often used to keep certain bits of a number
    and discard others -- and here, we want to keep the lowest 3 bits of `combo`
    and discard all the other bits. So my implementation of `bst` is
    `b = combo & 0b111`, which does exactly that.
3. `jnz`: If `a` is nonzero, set the instruction pointer to `operand` (and don't
increase it by 2 afterward like normal); otherwise, do nothing.
    - I use `if a` to test whether `a` is nonzero, `pointer = operand` to set
    the instruction pointer, and `continue` to ensure the `pointer += 2` part at
    the end of the loop is skipped. Super simple.
4. `bxc`: Do a bitwise XOR with `b` and `c`, and store the result back to `b`.
    - Similarly to `bxl`, `bxc` can be implemented as `b ^= c`.
5. `out`: Calculate `combo` modulo 8, and output the result.
    - Similarly to `bst`, I use a bitwise AND instead of a modulo to keep the
    lowest 3 bits. So my implementation of `out` is `yield combo & 0b111` --
    keeping in mind that we want to `yield` each outputted number!
6. `bdv`: Do the same calculation as `adv`, except store the result to `b`.
    - My implementation of `bdv` is `b = a >> combo` -- using the `>>` operator
    for the reasons I stated above.
7. `cdv`: Do the same calculation as `adv`, except store the result to `c`.
    - My implementation of `cdv` is `c = a >> combo` -- using the `>>` operator
    for the reasons I stated above.

```py title="2024\day17\solution.py" ins={"0 (adv)":13} ins={"1 (bxl)":15} ins={"2 (bst)":17} ins={"3 (jnz)":19-21} ins={"4 (bxc)":23} ins={"5 (out)":25} ins={"6 (bdv)":27} ins={"7 (cdv)":29}
from collections.abc import Iterator

def run(registers: tuple[int, ...], program: tuple[int, ...]) -> Iterator[int]:
    a, b, c = registers

    pointer = 0
    while pointer < len(program):
        opcode, operand = program[pointer : pointer + 2]
        combo = [0, 1, 2, 3, a, b, c][operand]

        match opcode:
            case 0:  # adv (A DiVide)
                a >>= combo
            case 1:  # bxl (B Xor Literal)
                b ^= operand
            case 2:  # bst (B STore)
                b = combo & 0b111
            case 3:  # jnz (Jump if Not Zero)
                if a:
                    pointer = operand
                    continue
            case 4:  # bxc (B Xor C)
                b ^= c
            case 5:  # out (OUTput)
                yield combo & 0b111
            case 6:  # bdv (B DiVide)
                b = a >> combo
            case 7:  # cdv (C DiVide)
                c = a >> combo
            case _:
                assert False, f"unexpected opcode {opcode}"

        pointer += 2
```

And just like that, the emulation function is _done_! We can now call
`run(registers, program)` to generate the outputs of our Historians'-computer
program. Then we'll want to convert the outputs to strings (which I do with the
[`map`](https://docs.python.org/3/library/functions.html#map) function), and
`str.join` them all together with commas.

```py title="2024\day17\solution.py" ins={11}
import re

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> str:
        registers, program = (
            tuple(map(int, re.findall(r"\d+", block)))
            for block in self.input
        )
        return ",".join(map(str, run(registers, program)))
```

Not so scary, right?

## Part 2

It seems the value of the A register is wrong, because the output was supposed
to look like _the program itself_; in other words, the program is supposed to be
a [quine](https://en.wikipedia.org/wiki/Quine_(computing))![^not-a-quine] Now
_this_ sounds pretty scary.

[^not-a-quine]: Technically it's _not_ a quine, because a quine is supposed to
output its own source code _given no input at all_... but this is a similar
concept to a quine.

It wouldn't be practical to brute-force all possible values of the A register,
as it would take a long time -- and possibly _never_ finish, if the provided
program ever happened to loop forever. So perhaps we can make this search easier
by noticing some non-trivial features of the puzzle input.[^non-trivial-features]
In other words... what is our program _actually_ doing?

[^non-trivial-features]: This is something I [usually](/solutions/2023/day/8)
[don't](/solutions/2023/day/20) [like](/solutions/2023/day/21) in an Advent of
Code puzzle, but this time I'll let it slide. It was _way_ more obvious to me
for today's puzzle that inspecting the input would be necessary.

Let's **disassemble** our program -- rewrite it so it uses instructions, rather
than opcode/operand numbers. For purposes of illustration, I'll be using the
program `0,3,5,4,3,0` from the example input;[^sharing-inputs] the features I
point out should still apply to the program from _your_ puzzle input. The result
should look a little something like this:

[^sharing-inputs]: I'm mainly doing this because there's a taboo against sharing
AoC puzzle inputs, which is especially enforced in [the Advent of Code subreddit](https://www.reddit.com/r/adventofcode/wiki/troubleshooting/no_asking_for_inputs/).
In my opinion, this is largely understandable; in this case, however, the
solution (and the path _to_ it) depends massively on what your exact input _is_,
which kneecaps my ability to explain it a bit.

| Opcode, Operand | Instruction |
| :-------------: | :---------: |
|       0,3       |   `adv 3`   |
|       5,4       |   `out a`   |
|       3,0       |   `jnz 0`   |

A few things to notice:

- The last instruction is `jnz 0`, which jumps back to the beginning of the
program if the A register is nonzero.
    - This means the whole program is one big loop, which always runs at least
    once, and continues to loop until the A register is zero at the end.
- The only instruction that changes the A register is an `adv 3` instruction,
which shifts A to the right by 3 bits on each pass of the loop.
    - This means the loop _won't_ run forever, because doing `adv 3` repeatedly
    will eventually shift out _all_ the bits of A and leave A at zero.
- Before the loop ends, an `out` instruction is performed, which outputs a
single number on each pass of the loop.
    - This means the length of the output will depend on how big A is; in other
    words, one number will be outputted for every 3-bit chunk of A.

This is a lot to take in, but the short version is: the program looks at **each
3-bit chunk of A from right to left**, and **outputs a single number per
chunk**. This suggests that we can use some approach similar to
[depth-first search](https://en.wikipedia.org/wiki/Depth-first_search)
(:abbr[DFS]{title="depth-first search"}) to build a working value of A one 3-bit
chunk at a time. Let's get to it.

---

First thing's first: I'll convert this solution to a unified `solve` function
for both parts.

```py title="2024\day17\solution.py" ins="solve" ins="tuple[str, int]" ins="program_output =" ins={15-16}
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[str, int]:
        registers, program = (
            tuple(map(int, re.findall(r"\d+", block)))
            for block in self.input
        )
        program_output = ",".join(map(str, run(registers, program)))

        ...

        min_quine_input = -1  # TODO Write find-quine-input code
        return program_output, min_quine_input
```

Now for the interesting part: searching for A values that'll give us back our
program as an output. The way I'll do this similar to :abbr[DFS]{title="depth-first search"};
in fact, I'll be using a _recursive_ function for this, which will take an A
value and the number $n$ of matched program digits so far.

- **Base case**: If (given this A value) the program's output matches the
program exactly, this A value is a "quine input".
- **Recursive case**: If (given this A value) the program's output matches the
last $n$ digits of the program, try appending another 3-bit chunk to A (in each
different possible way) and looking for a match of $n + 1$ digits. Otherwise,
we're at a dead end.

Because I'm rather fond of generator functions, I'm using yet another generator
function for this; it'll `yield` all of our "quine inputs", and we can pass them
directly to `min` to find the smallest one. Some notes about my implementation:

- `program[-n:]` gets the last `n` items of `program` -- _unless_ `n` is 0, in
which case it gets _every_ item of `program`. Because of this little quirk, I
do a check for whether `num_digits` is 0 _before_ I use it in this way.
- The way I append the next 3-bit chunk (which I call `next_a_bits`) to the A
value is by shifting A leftward by 3 bits, and then doing a `|` (bitwise OR)
with that chunk -- i.e. `(a_input << 3) | next_a_bits`. This is a pretty
standard way to do this with bitwise operations.

```py title="2024\day17\solution.py" ins={8-32} ins="min(quine_inputs())"
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[str, int]:
        ...
        # HACK To make the problem tractable, we must make several
        # assumptions about the structure of the program: it is a loop
        # that, on each pass until A is 0, consumes 3 bits of A and
        # outputs one number. This allows us to build an A value 3 bits
        # at a time until the output matches the program.
        ADV_OPERAND = 3  # Our program will include an "adv 3"
        _, b, c = registers

        def quine_inputs(
                a_input: int = 0,
                num_digits: int = 0,
        ) -> Iterator[int]:
            output = tuple(run((a_input, b, c), program))
            # If the output matches the program, this A is a quine input
            if output == program:
                yield a_input
                return
            # If the output matches the program's last few digits, try
            # assigning the next bits of A
            if num_digits == 0 or output == program[-num_digits:]:
                for next_a_bits in range(1 << ADV_OPERAND):
                    yield from quine_inputs(
                        (a_input << ADV_OPERAND) | next_a_bits,
                        num_digits + 1,
                    )

        min_quine_input = min(quine_inputs())
        return program_output, min_quine_input
```

Not the easiest thing in the world... but hey, we managed to figure out the
right input value without the Historians' computer breaking down! That's always
what you want when debugging a program.
