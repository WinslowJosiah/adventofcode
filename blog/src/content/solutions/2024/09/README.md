---
year: 2024
day: 9
title: "Disk Fragmenter"
slug: 2024/day/9
pub_date: "2026-05-16"
# concepts: []
---
## Part 1

We're trying to create more contiguous space on a filesystem with many file
blocks, and then calculate a checksum afterwards. It seems natural to represent
the filesystem as a list of "blocks", and the blocks as `int` file IDs (or
`None` if the block doesn't exist). First, let's write a simple function for
calculating the checksum of a series of blocks.

```py title="2024\day09\solution.py"
from collections.abc import Iterable

type Block = int | None

def checksum_blocks(blocks: Iterable[Block]) -> int:
    return sum(
        address * block
        for address, block in enumerate(blocks)
        if block is not None
    )
```

The next step is to create the disk using the disk map. I'll be using two
helpful functions from the builtin `itertools` module:

- `itertools.batched(iterable, n)` takes an iterable, and returns it back in
non-overlapping "batches" of size `n` (with the last batch possibly being
smaller). We can use this to iterate through the file sizes and gap sizes of the
disk map -- though here, we have to fill in an extra `"0"` digit so that every
batch has a size of 2.
- `itertools.repeat(object, times)` takes an object, and returns that object
repeated the specified number of times. We can use this to extend the disk list
by a certain number of file/gap blocks.

Note that I'm wrapping my `batched` call in `enumerate`; this allows for each
batch of file and gap sizes to be counted from 0 onwards, and this count can be
directly used as the file ID for this batch's file.

```py title="2024\day09\solution.py"
from itertools import batched, repeat
...

class Solution(TextSolution):
    def part_1(self) -> int:
        assert len(self.input) % 2 == 1
        digits = map(int, self.input + "0")  # make last gap be 0
        # A disk is a list of blocks; a block is a file ID or None
        disk: list[Block] = []
        for file_id, (file_size, gap_size) in enumerate(batched(digits, 2)):
            disk.extend(repeat(file_id, file_size))
            disk.extend(repeat(None, gap_size))
        ...
```

Now for actually compacting the files. We'll use two pointers in the disk that
move towards each other: one "writer" starting from the left that points to a
gap, and one "reader" starting from the right that points to a file.[^part-1-approach]

Once both pointers find what they're looking for, we can swap the items they're
pointing to. And if the pointers ever pass each other (which I check as the
"writer" finds a suitable gap), we're done.

[^part-1-approach]: My initial Part 1 approach didn't use a "reader" pointer.
Instead, it used the last item in the list as the implied "pointer", which meant
I could use the [`pop`](https://docs.python.org/3/library/stdtypes.html#sequence.pop)
method of lists to both obtain the rightmost file block _and_ get rid of it. The
resulting code looked something like this:

    ```py
    ...
    writer = 0
    while True:
        try:
            writer = disk.index(None, writer)
        except ValueError:
            break

        while (block := disk.pop()) is None:
            if writer >= len(disk):
                break
        else:
            disk[writer] = block
    ...
    ```

    Part of me liked this more than the two-pointers approach, because the
    latter reminds me of what I'd see in a C program (and in general, the more
    C-like a Python program looks, the less "Pythonic" it is). However, I never
    liked how I handled having the "writer" find gaps; it's generally bad
    practice to throw and catch exceptions when you don't need to, and a rewrite
    that avoids doing this would be slightly longer and less [beautiful](https://pep20.org/#beautiful).

    My main reason for using the two-pointers approach in this writeup is that
    it makes the logic more [explicit](https://pep20.org/#explicit), and it can
    be adapted (with some care) to Part 2 without changing how it fundamentally
    works.

```py title="2024\day09\solution.py"
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...
        # The reader will scan backwards for files
        reader = len(disk) - 1
        # The writer will scan forwards for gaps
        writer = 0
        while True:
            # Find the next file block
            while (file_id := disk[reader]) is None:
                reader -= 1

            # Find the next gap before the file
            while writer < reader:
                if disk[writer] is None:
                    break
                writer += 1
            else:
                # Stop looping if no suitable gap is found
                break

            # Remove the file and move it to the gap
            disk[writer] = file_id
            disk[reader] = None
        ...
```

:::tip
The loop that finds the next file block has a peculiar feature: the `:=`
operator (nicknamed the "walrus operator"). It allows for a variable to be
stored to and reused in the same expression.

When used in certain contexts, this operator can make some pieces of code more
elegant. For example, the equivalent loop _without_ this operator would look
like this:

```py
file_id = disk[reader]
while file_id is None:
    reader -= 1
    file_id = disk[reader]
```

I'd say the version with `:=` is an improvement.
:::

At this point, the files have been compacted, and the disk can be checksummed.

```py title="2024\day09\solution.py"
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...
        return checksum_blocks(disk)
```

## Part 2

Now instead of moving individual blocks to fill gaps, we're moving entire files.
This will be made easier if we change our representation of the filesystem, from
a list of blocks to a list of "chunks" -- entire files, or entire contiguous
gaps.[^part-2-approach] These chunks will essentially be blocks with sizes, so
we can use the builtin [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
module to create a simple `Chunk` class with a block and a size.

[^part-2-approach]: My initial approach actually stuck with the block-list
representation; in fact, after some optimizations, it was much faster than using
the chunk-list representation -- ~0.8 seconds versus ~2.8 seconds on my machine.
But for this writeup, it felt too C-like and imperative for my liking, not as
[beautiful](https://pep20.org/#beautiful) as the chunk-list approach in my
opinion, and [harder to explain](https://pep20.org/#hard) once the optimizations
were included.

```py title="2024\day09\solution.py" ins={1,7-12} ins="chunks" ins=/\\[(Chunk)\\]/ ins="append(Chunk"
from dataclasses import dataclass
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        # NOTE A "chunk" is either a file (if its block value is an int)
        # or a gap (if its block value is None).
        @dataclass
        class Chunk:
            block: Block
            size: int

        assert len(self.input) % 2 == 1
        digits = map(int, self.input + "0")  # make last gap be 0
        # A disk is a list of chunks
        disk: list[Chunk] = []
        for file_id, (file_size, gap_size) in enumerate(batched(digits, 2)):
            disk.append(Chunk(file_id, file_size))
            disk.append(Chunk(None, gap_size))
        ...
```

The code that handles the "reader" and "writer" pointers will have to be changed
to account for this new chunk-list format, but the general idea is the same; the
"reader" will start on the right and look for files, the "writer" will start on
the left and look for gaps, and each file will be moved into a gap if it can.

First, instead of having the reader read any file block it finds, we need the
reader to read the files from highest ID to lowest ID. The file IDs are
sequential, so we can simply get the highest ID from the second-to-last block of
the disk, and use `range` to loop over the file IDs going down.

```py title="2024\day09\solution.py" ins={7-10,16} del={14-15} ins=/file (chunk)/ ins=/(file) :=/ ins=".block != file_id"
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        ...
        # NOTE The last chunk is a gap; the chunk before last is the
        # file with the largest file ID.
        max_file_id = disk[-2].block
        assert max_file_id is not None

        # The reader will scan backwards for files
        reader = len(disk) - 1
        # The writer will scan forwards for gaps
        writer = 0
        for file_id in range(max_file_id, -1, -1):
            # Find the next file chunk
            while (file := disk[reader]).block != file_id:
                reader -= 1
            ...
```

:::note
We're _not_ initializing the writer outside of the main loop like before; we
will instead do this _inside_ the main loop.

For Part 1, we could assume that there will be no suitable gaps before the
writer pointer, because all preceding gaps would've been filled; for Part 2,
however, it _could_ be the case that the earliest suitable gap is to the _left_
of the current writer pointer, so the only reliable way to find it is to start
the search from the far left every time.
:::

Next, instead of having the writer search for the first gap _period_, we need to
search for the first gap where the size is at least the size of the file. (And
the `break` that we do if there are no suitable gaps should be turned into a
`continue`, because we want every file to be processed this time.)

```py title="2024\day09\solution.py" ins={9-10,14-15} ins="large enough" ins="Move on" ins="continue"
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        ...
        for file_id in range(max_file_id, -1, -1):
            ...
            # The writer will scan forwards for gaps
            writer = 0
            # Find the next large enough gap before the file
            while writer < reader:
                if (
                    (gap := disk[writer]).block is None
                    and gap.size >= file.size
                ):
                    break
                writer += 1
            else:
                # Move on if no suitable gap is found
                continue
            ...
```

Lastly, the moving of the file must be handled differently. We'll do it in the
following way:

1. Insert the file into the writer's position using the `list.insert` method.
2. Create a gap of the proper size at the reader's position. _(Note: the reader
pointer should be increased by 1 because of the insertion step!)_
3. Make the gap size smaller by the size of the inserted file.

```py title="2024\day09\solution.py" {"1":10} {"2":11-12} {"3":14}
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        ...
        for file_id in range(max_file_id, -1, -1):
            ...
            # Remove the file and move it to the gap
            disk.insert(writer, file)
            reader += 1  # the insert shifts the index by 1
            disk[reader] = Chunk(None, file.size)
            # Reduce the size of the gap to account for the file
            gap.size -= file.size
        ...
```

The only loose end to tie up is the checksumming process. Our checksum function
takes a series of blocks, so we have to take our list of chunks and convert it
to a series of blocks.

`itertools` will help us here again; its `chain.from_iterable` function can be
used to combine many iterables of items into a single iterable. The thing we'll
be combining is a generator that takes each chunk in the disk and expands it,
using the same `repeat` function we had used to build the disk in Part 1.

```py title="2024\day09\solution.py" ins="chain, " ins={9-11}
from itertools import batched, chain, repeat
...

class Solution(TextSolution):
    ...
    def part_2(self) -> int:
        ...
        return checksum_blocks(
            chain.from_iterable(
                repeat(chunk.block, chunk.size) for chunk in disk
            )
        )
```

Part 2 ends up taking a couple seconds on my machine to finish, and that's
probably due to all the `list.insert` calls (which get slow if the list is big
and the index is early). It's not too bad, though, and I've _definitely_ seen
worse.
