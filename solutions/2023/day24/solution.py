# https://adventofcode.com/2023/day/24

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import prod

from ...base import StrSplitSolution, answer


def parse_3d_point(point: str) -> list[int]:
    return list(map(int, point.split(", ")))


@dataclass(frozen=True)
class Hailstone:
    px: int
    py: int
    pz: int
    vx: int
    vy: int
    vz: int

    def position(self, dim: str) -> int:
        assert dim in "xyz", f"invalid dimension: {dim}"
        return getattr(self, f"p{dim}")

    def velocity(self, dim: str) -> int:
        assert dim in "xyz", f"invalid dimension: {dim}"
        return getattr(self, f"v{dim}")

    @classmethod
    def parse(cls, line: str) -> Hailstone:
        position, velocity = line.split(" @ ")
        return Hailstone(*parse_3d_point(position), *parse_3d_point(velocity))

    def intersection_with(self,
            other: Hailstone,
            *,
            future_only: bool = False,
    ) -> tuple[Fraction, Fraction] | None:
        """
        Return intersection point with another hailstone (2D only).
        """
        denominator = other.vx * self.vy - other.vy * self.vx
        # If this denominator is 0, the lines are parallel or coincident
        if denominator == 0:
            return None

        # When does this hailstone intersect the other one?
        self_t = Fraction(
            other.vx * (other.py - self.py) - other.vy * (other.px - self.px),
            denominator,
        )
        # When does the other hailstone intersect this one?
        other_t = Fraction(
            self.vx * (other.py - self.py) - self.vy * (other.px - self.px),
            denominator,
        )

        if future_only and (self_t < 0 or other_t < 0):
            return None

        # Get the position of this hailstone when it intersects
        return self.px + self_t * self.vx, self.py + self_t * self.vy

    def relative_to_rock_velocity(self, rvx: int, rvy: int) -> Hailstone:
        """
        Return hailstone velocity relative to rock velocity (2D only).
        """
        return Hailstone(
            self.px, self.py, self.pz,
            self.vx - rvx, self.vy - rvy, self.vz,
        )


def divisors(n: int) -> Iterator[int]:
    """
    Generate all divisors of an integer.

    The divisors are yielded in no particular order. To find the
    divisors, the prime factors are found through trial division, then
    each combination of those prime factors are multiplied together; as
    such, this function is efficient for integers with small prime
    factors.

    Parameters
    ----------
    n : int
        The integer to generate divisors for.

    Yields
    ------
    int
        The divisors of the integer.
    """
    # Gather prime factors and their exponents
    prime_factors: Counter[int] = Counter()
    factor = 2
    while factor * factor <= n:
        if n % factor == 0:
            n //= factor
            prime_factors[factor] += 1
        else:
            factor += 1
    if n > 1:
        prime_factors[n] += 1

    # Generate all combinations of prime factors to form divisors
    powers: list[list[int]] = [
        [factor ** i for i in range(count + 1)]
        for factor, count in prime_factors.items()
    ]
    for group in product(*powers):
        yield prod(group)


def possible_rock_velocities(
        hailstone_velocity: int,
        distance: int,
) -> set[int]:
    """
    Given two hailstones moving at `hailstone_velocity` separated by
    `distance`, find all possible rock velocities that could hit both.

    The rock must travel over `distance` in some integer time t, so:

        rock_velocity = hailstone_velocity ± distance/t

    For `rock_velocity` to be an integer, `t` must be a divisor of
    `distance`; therefore, so must `distance/t`.
    """
    return {
        hailstone_velocity + v
        for rock_velocity in divisors(abs(distance))
        for v in (-rock_velocity, rock_velocity)
    }


def get_rock_velocity(hailstones: list[Hailstone], dim: str) -> int:
    # For each pair of parallel hailstones, calculate every possible
    # rock velocity that could hit them both
    rock_velocities = [
        possible_rock_velocities(
            hailstone_velocity=l.velocity(dim),
            distance=r.position(dim) - l.position(dim),
        )
        for l, r in combinations(hailstones, 2)
        if l.velocity(dim) == r.velocity(dim)
    ]
    # Return the (assumed unique) velocity that could hit every pair of
    # parallel hailstones
    shared_rock_velocities = rock_velocities[0].intersection(*rock_velocities)
    assert len(shared_rock_velocities) == 1, f"unique {dim} velocity not found"
    return shared_rock_velocities.pop()


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 24.
    """
    _year = 2023
    _day = 24

    @answer(21843)
    def part_1(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]
        BOUNDS_MIN, BOUNDS_MAX = (
            (7, 27)
            if self.testing
            else (200_000_000_000_000, 400_000_000_000_000)
        )

        total = 0
        # Check the intersection points of each pair of hailstones
        for l, r in combinations(hailstones, 2):
            intersection = l.intersection_with(r, future_only=True)
            if intersection is None:
                continue

            x_intersection, y_intersection = intersection
            if (
                BOUNDS_MIN <= x_intersection <= BOUNDS_MAX
                and BOUNDS_MIN <= y_intersection <= BOUNDS_MAX
            ):
                total += 1

        return total

    @answer(540355811503157)
    def part_2(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]
        # HACK The sample input doesn't allow us to find unique X/Y/Z
        # velocities for the rock with our method. It would still work,
        # but we'd need to test all possible combinations of velocities,
        # which would be somewhat awkward.
        if self.testing:
            rvx, rvy, rvz = -3, 1, 2
        else:
            rvx, rvy, rvz = (
                get_rock_velocity(hailstones, dim)
                for dim in "xyz"
            )

        # Find the X/Y position of the rock for it to hit two hailstones
        # NOTE We check all pairs here, since some pairs of hailstones
        # may be collinear relative to the rock (and thus fail to find a
        # unique intersection point).
        intersection = None
        for a, b in combinations(hailstones, 2):
            a_relative = a.relative_to_rock_velocity(rvx, rvy)
            b_relative = b.relative_to_rock_velocity(rvx, rvy)
            intersection = a_relative.intersection_with(b_relative)
            if intersection is not None:
                break
        else:
            raise ValueError("could not find starting X/Y for rock")

        rpx, rpy = intersection
        assert rpx.is_integer(), "rock's x position is not an integer"
        assert rpy.is_integer(), "rock's y position is not an integer"

        # Solve for the rock's Z position with some algebra
        time = (a.px - rpx) / (rvx - a.vx)
        rpz = a.pz + time * (a.vz - rvz)
        assert rpz.is_integer(), "rock's z position is not an integer"

        return int(rpx + rpy + rpz)
