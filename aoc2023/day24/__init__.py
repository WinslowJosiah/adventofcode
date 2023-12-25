from collections.abc import Iterable


def aoc2023_day24_part1(lines: Iterable[str]) -> int:
    from itertools import combinations

    test_area_min = 200_000_000_000_000
    test_area_max = 400_000_000_000_000

    # Gather list of hailstones
    hailstones = [
        tuple(
            tuple(map(int, part.split(", ")))
            for part in line.split("@")
        )
        for line in lines
    ]

    total = 0
    # For each pair of hailstones
    for hailstone1, hailstone2 in combinations(hailstones, 2):
        (h1x, h1y, _), (h1vx, h1vy, _) = hailstone1
        (h2x, h2y, _), (h2vx, h2vy, _) = hailstone2

        h1_slope = h1vy / h1vx
        h2_slope = h2vy / h2vx
        # If hailstone paths are parallel, skip this pair
        if h1_slope == h2_slope:
            continue

        # The point at which the two hailstone paths cross can be
        # calculated with a bit of algebra
        h1_y_int = h1y - h1_slope * h1x
        h2_y_int = h2y - h2_slope * h2x
        crossing_x = (h2_y_int - h1_y_int) / (h1_slope - h2_slope)
        crossing_y = h1_slope * crossing_x + h1_y_int

        # If crossing occurred outside of test area, skip this pair
        if not (
            test_area_min <= crossing_x <= test_area_max
            and test_area_min <= crossing_y <= test_area_max
        ):
            continue

        # If crossing occurred in the past, skip this pair
        if any(
            vx < 0 and x < crossing_x
            or vx > 0 and x > crossing_x
            or vy < 0 and y < crossing_y
            or vy > 0 and y > crossing_y
            for (x, y, _), (vx, vy, _) in (hailstone1, hailstone2)
        ):
            continue

        # These hailstones cross in the test area
        total += 1

    return total


def aoc2023_day24_part2(lines: Iterable[str]) -> int:
    # NOTE: I wanted not to use sympy for three reasons.
    # 1. It's an external library.
    # 2. It makes my IDE slow.
    # 3. It makes the type checker very unhappy.
    # But it's honestly the easiest way to get a solution for Part 2.
    from sympy.core.expr import Expr
    from sympy.core.symbol import Symbol, symbols  # type: ignore
    from sympy.solvers import solve  # type: ignore

    # Gather list of hailstones
    hailstones = [
        tuple(
            tuple(map(int, part.split(", ")))
            for part in line.split("@")
        )
        for line in lines
    ]

    xr, yr, zr, vxr, vyr, vzr = symbols("xr yr zr vxr vyr vzr")
    equations: list[Expr] = []
    answers: list[dict[Symbol, Expr]] = []
    # For each hailstone
    for i, ((x, y, z), (vx, vy, vz)) in enumerate(hailstones):
        # NOTE: The positions of the hailstone and rock must be equal
        # after some time t has passed. We can factor out the factor of
        # t with a bit of algebra, and simply check whether 3 ratios
        # based on the x/y/z coordinates equal each other.
        equations.append(
            (xr - x) * (vy - vyr) - (yr - y) * (vx - vxr)
        )
        equations.append(
            (yr - y) * (vz - vzr) - (zr - z) * (vy - vyr)
        )

        # NOTE: In practice, there will only be a solution after 3 or
        # more hailstones.
        if i < 2:
            continue

        # Gather all solutions which include all 6 variables, where all
        # values are integers
        answers = [
            soln
            for soln in solve(equations, dict=True)  # type: ignore
            if (
                len(soln) == 6  # type: ignore
                and all(v.is_integer for v in soln.values())  # type: ignore
            )
        ]
        # If there is exactly one solution, we're done
        if len(answers) == 1:
            break

    assert len(answers) == 1
    answer = answers[0]
    # Add the coordinates of our solution
    return int(answer[xr] + answer[yr] + answer[zr])  # type: ignore


parts = (aoc2023_day24_part1, aoc2023_day24_part2)
