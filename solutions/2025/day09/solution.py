# https://adventofcode.com/2025/day/9

from functools import cache
from itertools import combinations, pairwise
from typing import cast

from ...base import StrSplitSolution, answer
from ...utils.grids import GridPoint


@cache
def point_in_polygon(point: GridPoint, polygon: tuple[GridPoint, ...]) -> bool:
    x, y = point
    padded_polygon = [*polygon, polygon[0]]

    # Check if point is exactly on an edge (which counts as inside)
    for (x1, y1), (x2, y2) in pairwise(padded_polygon):
        assert x1 == x2 or y1 == y2, "polygon is not axis-aligned"
        # Vertical edge
        if x1 == x and min(y1, y2) <= y <= max(y1, y2):
            return True
        # Horizontal edge
        if y1 == y and min(x1, x2) <= x <= max(x1, x2):
            return True

    # NOTE Consider a horizontal ray going rightward from the point, and
    # count the edges it crosses; if it's even, the point is outside,
    # and if it's odd, the point is inside. This is the "even-odd rule".
    crossings = 0
    for (x1, y1), (x2, y2) in pairwise(padded_polygon):
        # Horizontal edges will never be crossed
        if y1 == y2:
            continue
        # This vertical edge is crossed if its X is to the right and our
        # horizontal ray is within its Y range
        if x < x1 and min(y1, y2) < y <= max(y1, y2):
            crossings += 1

    # An odd number of crossings means we are inside
    return crossings % 2 == 1


def rectangle_in_polygon(
        corners: tuple[GridPoint, GridPoint],
        polygon: tuple[GridPoint, ...],
) -> bool:
    (rx1, ry1), (rx2, ry2) = corners
    # Sort rectangle X and Y values
    (rx1, rx2), (ry1, ry2) = sorted([rx1, rx2]), sorted([ry1, ry2])

    rectangle = ((rx1, ry1), (rx2, ry1), (rx2, ry2), (rx1, ry2))
    # Check if this rectangle's corners are all inside the polygon
    if not all(point_in_polygon(p, polygon) for p in rectangle):
        return False

    # HACK Here, we check that no edge of the polygon goes inside the
    # rectangle. This is technically incorrect - if two adjacent polygon
    # edges go inside the rectangle, no rectangle point would be outside
    # the polygon - but that edge case doesn't happen in our input.
    padded_polygon = [*polygon, polygon[0]]
    for (px1, py1), (px2, py2) in pairwise(padded_polygon):
        assert px1 == px2 or py1 == py2, "polygon is not axis-aligned"
        # Sort polygon X and Y values
        (px1, px2), (py1, py2) = sorted([px1, px2]), sorted([py1, py2])
        # Check if this polygon edge overlaps the rectangle's interior
        # (which happens if its X ranges and Y ranges intersect)
        if px1 < rx2 and rx1 < px2 and py1 < ry2 and ry1 < py2:
            return False

    # HACK The preceding tests will incorrectly say the empty inside of
    # a horseshoe-like shape is "inside" the polygon. This shape occurs
    # in our input, but doesn't affect our answer because it's so thin;
    # nevertheless, to detect it, we also check the rectangle's "inner
    # corners" (if it is big enough to have any).
    if rx2 - rx1 > 1 and ry2 - ry1 > 1:
        inner_corners = (
            (rx1 + 1, ry1 + 1),
            (rx2 - 1, ry1 + 1),
            (rx2 - 1, ry2 - 1),
            (rx1 + 1, ry2 - 1),
        )
        if not all(point_in_polygon(p, polygon) for p in inner_corners):
            return False

    return True


def rectangle_area(corners: tuple[GridPoint, GridPoint]) -> int:
    (x1, y1), (x2, y2) = corners
    return (abs(x2 - x1) + 1) * (abs(y2 - y1) + 1)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2025 Day 9.
    """
    _year = 2025
    _day = 9

    _cached_functions = (point_in_polygon,)

    @answer((4782151432, 1450414119))
    def solve(self) -> tuple[int, int]:
        points = tuple(
            cast(GridPoint, tuple(map(int, line.split(","))))
            for line in self.input
        )
        # HACK This enforces an assumption made in rectangle_in_polygon.
        padded_points = [*points, points[0]]
        assert all(
            abs(x2 - x1) > 1 or abs(y2 - y1) > 1
            for (x1, y1), (x2, y2) in pairwise(padded_points)
        ), "some edges are too close together"

        max_area, max_contained_area = 0, 0
        for corners in combinations(points, 2):
            area = rectangle_area(corners)
            if area > max_area:
                max_area = area
            if area > max_contained_area:
                if rectangle_in_polygon(corners, points):
                    max_contained_area = area

        return max_area, max_contained_area
