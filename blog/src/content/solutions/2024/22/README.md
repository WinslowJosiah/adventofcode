---
year: 2024
day: 22
title: "Monkey Market"
slug: 2024/day/22
pub_date: "2026-11-26"
# concepts: []
---
## Part 1

Talk about "monkey business"! We're looking at some kind of exchange market
operated by monkeys, and we have to calculate the "secret numbers" each buyer
will use to determine their selling prices.

Each secret number is generated based on the previous secret number, and the
puzzle prompt's description of how the process works is fairly straightforward
to implement (if you remember that `^` is the [bitwise XOR](https://en.wikipedia.org/wiki/Bitwise_operation#XOR)
operator in Python). However, I ended up implementing it in a slightly different
way to highlight a connection to real-world [pseudorandom number generators](https://en.wikipedia.org/wiki/Pseudorandom_number_generator)
(a.k.a. :abbr[PRNG]{title="pseudorandom number generator"}s).

- Instead of multiplying and integer-dividing by 64, 32, and 2048 (which are all
powers of 2), I decided to use [bit shifts](https://en.wikipedia.org/wiki/Bitwise_operation#Bit_shifts)
(`<<` and `>>` in Python). Shifting a number $n$ bits to the left is the same as
multiplying by $2^n$, and shifting a number $n$ bits to the right is the same as
integer-dividing by $2^n$.
- Instead of doing a modulo by 16777216, I decided to do a [bitwise AND](https://en.wikipedia.org/wiki/Bitwise_operation#AND)
(`&` in Python). 16777216 is exactly $2^{24}$, so the purpose of the modulo is
to keep the resulting number within 24 bits. Doing a bitwise AND with `0xffffff`
-- a number with its lowest 24 bits all set -- accomplishes the same purpose.

```py title="2024\day22\solution.py"
def next_secret(secret: int) -> int:
    # NOTE The technical name for this is an Xorshift random number
    # generator; the operations have been replaced with equivalent
    # bitwise operators, so the resemblance is clearer.
    secret = (secret ^ (secret << 6)) & 0xffffff
    secret = (secret ^ (secret >> 5)) & 0xffffff
    return (secret ^ (secret << 11)) & 0xffffff
```

In this form, the secret number generator looks like a specific kind of :abbr[PRNG]{title="pseudorandom number generator"}
that is used in the real world -- an [Xorshift](https://en.wikipedia.org/wiki/Xorshift)
random number generator, one of the fastest kinds of :abbr[PRNG]{title="pseudorandom number generator"}s
out there. That's pretty neat.

Once we have our `next_secret` function, we can simply call it 2000 times for
each secret number in our input, feeding in the previous secret number each
time, and add the resulting secret number to a running total.

```py title="2024\day22\solution.py"
...

class Solution(IntSplitSolution):
    def part_1(self) -> int:
        total = 0
        for secret in self.input:
            # Generate this buyer's 2000th secret
            for _ in range(2000):
                secret = next_secret(secret)
            total += secret
        return total
```

This gives us an answer in no time flat. We have successfully simulated the
secret number system... but how do we use it to our advantage in the market?

## Part 2

We've hired a monkey to negotiate in the market, and we're going to instruct the
monkey to sell to each buyer only when it sees a specific sequence of four price
changes from that buyer. We want to choose that price-change sequence such that
we get the highest profit possible.

Essentially, we'll want to map price-change sequences to banana profit totals,
keeping a tally of the profit we'd get from each price-change sequence we see as
we go through each buyer. The most convenient way to do this is with a
[`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter),
which we'll use to count the bananas we'd earn as profit for each price-change
sequence from the whole market; our answer will then be the highest of these
market profit totals.

```py title="2024\day22\solution.py" ins={1}
from collections import Counter
...

class Solution(IntSplitSolution):
    ...
    def part_2(self) -> int:
        # Each price-change sequence will have an associated profit from
        # the entire market of buyers
        market_profits: Counter[tuple[int, ...]] = Counter()
        ...
```

The price associated with each secret number is simply the ones digit of that
secret number -- in other words, the secret number modulo 10. (I decided to
create a small function for this to avoid some repetition.) We'll create a
`prices` list to hold all of this buyer's prices, starting with the price for
the first secret number and continuing with 2000 more prices for 2000 more
secret numbers (using a similar loop to Part 1).

```py title="2024\day22\solution.py"
...

class Solution(IntSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        def price(secret: int) -> int:
            return secret % 10

        for secret in self.input:
            prices = [price(secret)]
            # Generate 2000 of this buyer's secrets to convert to prices
            for _ in range(2000):
                secret = next_secret(secret)
                prices.append(price(secret))
            ...
        ...
```

We'll also create a variable called `changes` to hold the 4 most recent price
changes from this buyer... but what _exact_ data structure should we use? We
want it to act like a sliding window; at each price change we see, we want to
append the latest one to the end, and also remove the earliest one from the
beginning to keep the length at 4. This is perfectly suited for
[`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
-- and as it turns out, specifying the `maxlen` of the `deque` as 4 will keep
the length at 4 automatically, giving us the sliding window behavior we want
without having to remove items manually.

```py title="2024\day22\solution.py" ins=", deque"
from collections import Counter, deque
...

class Solution(IntSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        for secret in self.input:
            ...
            # The price changes will be a sliding window
            changes: deque[int] = deque(maxlen=4)
            assert changes.maxlen is not None
            ...
        ...
```

Now, to find which sequences of price changes map to which banana profits from
this buyer, we'll need to simulate all of their price changes and note which
sequences of price changes lead to which buying prices. This simulation will use
[`itertools.pairwise`](https://docs.python.org/3/library/itertools.html#itertools.pairwise)
to iterate through all adjacent pairs of prices in our `prices` list (so we can
get the price change with a simple subtraction).

Going into this loop, we'll be updating a `dict` called `buyer_profits` that
holds the profit we'll see from this buyer for each price-change sequence. On
each iteration, we'll do the following:

- First, we'll calculate the latest change in price -- the current price minus
the previous price -- and append it to `changes`.
- Next, we'll check whether we have enough price changes saved up; we want at
least 4, the same as the `maxlen` we set before. If we do, then we'll update
`buyer_profits` by recording the current price for this sequence of changes --
but only if we _haven't_ recorded anything for this sequence of changes before.
    - We have to convert `changes` to a `tuple` to make it a valid key for a
    `dict`.
    - Setting a value for some key in a `dict` only if the key _isn't_ in the
    `dict` can be done directly with [`dict.setdefault`](https://docs.python.org/3/builtins/stdtypes.html#dict.setdefault),
    rather than the slightly longer `if` statement you'd otherwise need.

```py title="2024\day22\solution.py" ins={1}
from itertools import pairwise
...

class Solution(IntSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        for secret in self.input:
            ...
            # Each price-change sequence will have an associated profit
            # from this buyer
            buyer_profits: dict[tuple[int, ...], int] = {}
            # For each pair of prices (and thus, for each price change)
            for prev_price, curr_price in pairwise(prices):
                changes.append(curr_price - prev_price)
                if len(changes) >= changes.maxlen:
                    # If this price-change sequence wasn't seen before,
                    # associate it with the buyer's current price
                    buyer_profits.setdefault(tuple(changes), curr_price)
            ...
        ...
```

Once the possible profits we could get from this buyer are known, we're almost
done! The last thing we need to do for this buyer is add those profits to our
market-profits `Counter`, which we can do using the [`Counter.update`](https://docs.python.org/3/library/collections.html#collections.Counter.update)
method. And then once we're done checking all buyers and their secret numbers,
we can get the highest banana count from our market-profits `Counter` with `max`
to get the answer we're after.

```py title="2024\day22\solution.py"
...

class Solution(IntSplitSolution):
    ...
    def part_2(self) -> int:
        ...
        for secret in self.input:
            ...
            # Add all possible buyer profits to the profit totals
            market_profits.update(buyer_profits)

        return max(market_profits.values())
```

We had to be a bit careful, but we eventually solved the problem. The monkey is
off our back -- and is now trading in the market. Let's wish it luck!
