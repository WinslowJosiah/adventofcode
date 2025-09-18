from collections.abc import Callable, Iterable, Iterator
from enum import IntEnum
from itertools import pairwise, product
from typing import Literal, NamedTuple, Self


type GridPoint = tuple[int, int]
type Grid[Item] = dict[GridPoint, Item]


_OFFSETS = list(product((-1, 0, 1), repeat=2))


def neighbors(
        center: GridPoint,
        num_directions: int = 8,
        *,
        grid_size: int | None = None,
        grid_width: int | None = None,
        grid_height: int | None = None,
        diagonals: bool = False,
) -> Iterator[GridPoint]:
    """
    Return the set of `GridPoint`s that are "neighbors" of `center`.

    `num_directions` must be one of the following values, which result
    in the following neighbors being yielded:
    - 4: The points in the N, W, E, and S directions (or the NW, NE, SW,
    and SE directions, if `diagonals` is true).
    - 8: The points in the NW, N, NE, W, E, SW, S, and SE directions.
    - 9: The points yielded when `num_directions` is 8, and the central
    point itself.

    If `grid_width` and/or `grid_height` are provided, neighbors will be
    yielded only if they are within the provided bounds. `grid_size` can
    be used instead of `grid_width` and `grid_height` if the grid is
    square.

    Parameters
    ----------
    center : GridPoint
        Grid point to find neighbors of.
    num_directions : {4, 8, 9}, default 8
        Number of directions to find neighbors in.
    grid_size : int, optional
        Size of square grid (number of rows/columns). If provided,
        `grid_width` and `grid_height` must not be provided.
    grid_width : int, optional
        Width of grid (number of columns). If provided, `grid_size` must
        not be provided.
    grid_height : int, optional
        Height of grid (number of rows). If provided, `grid_size` must
        not be provided.
    diagonals : bool, default False
        If true and `num_directions` is 4, only the diagonally adjacent
        neighbors are yielded.

    Yields
    ------
    GridPoint
        Neighbor of center grid point.
    """
    assert num_directions in {4, 8, 9}
    if diagonals:
        assert (
            num_directions == 4
        ), "diagonals is only valid if num_directions == 4"

    if grid_size is not None:
        assert (
            grid_width is None and grid_height is None
        ), "specify only grid_size or grid_width/grid_height"
    if grid_width is not None or grid_height is not None:
        assert (
            grid_size is None
        ), "specify only grid_size or grid_width/grid_height"
    is_bounded = (
        grid_size is not None
        or grid_width is not None
        or grid_height is not None
    )

    for offset_r, offset_c in _OFFSETS:
        # If self is not needed, skip
        if num_directions != 9 and not (offset_r or offset_c):
            continue
        # If asking for diagonals and offset is not diagonal, skip
        if diagonals and not (offset_r and offset_c):
            continue
        # If asking for orthogonals and offset is diagonal, skip
        if num_directions == 4 and not diagonals and offset_r and offset_c:
            continue

        next_r, next_c = add_points(center, (offset_r, offset_c))

        # If using bounded size and new point is negative, skip
        if is_bounded and (next_r < 0 or next_c < 0):
            continue
        # If new point is out of bounds, skip
        if grid_size is not None and (
            next_r >= grid_size or next_c >= grid_size
        ):
            continue
        if grid_width is not None and next_c >= grid_width:
            continue
        if grid_height is not None and next_r >= grid_height:
            continue

        yield next_r, next_c


def add_points(a: GridPoint, b: GridPoint) -> GridPoint:
    """
    Return the result of adding the coordinates of two `GridPoint`s.

    Parameters
    ----------
    a : GridPoint
        First grid point.
    b : GridPoint
        Second grid point.

    Returns
    -------
    GridPoint
        Result of adding `b`'s coordinates to `a`'s coordinates.
    """
    return a[0] + b[0], a[1] + b[1]


def subtract_points(a: GridPoint, b: GridPoint) -> GridPoint:
    """
    Return the result of subtracting the coordinates of two
    `GridPoint`s.

    Parameters
    ----------
    a : GridPoint
        First grid point.
    b : GridPoint
        Second grid point.

    Returns
    -------
    GridPoint
        Result of subtracting `b`'s coordinates from `a`'s coordinates.
    """
    return a[0] - b[0], a[1] - b[1]


def taxicab_distance(a: GridPoint, b: GridPoint) -> int:
    """
    Return the taxicab distance between two `GridPoint`s (the length of
    the shortest path along a rectangular grid).

    Parameters
    ----------
    a : GridPoint
        First grid point.
    b : GridPoint
        Second grid point.

    Returns
    -------
    int
        Taxicab distance between `a` and `b`.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def parse_grid[Item](
        raw_grid: list[str],
        item_factory: Callable[[str], Item] = str,
        *,
        ignore_chars: Iterable[str] = "",
) -> Grid[Item]:
    """
    Convert a list of string lines to a grid.

    The grid is implemented as a `dict` mapping `GridPoint`s to grid
    items. Each line will correspond to a row in the grid, and each
    character of a line will be used to fill the row.

    Grid items are created by passing each character to `item_factory`
    as an argument (`str` by default, which leaves the character
    unchanged). If `ignore_chars` is provided, any character in it will
    be ignored when filling in the grid.

    Parameters
    ----------
    raw_grid : list of str
        List of string lines.
    item_factory : callable, default `str`
        A callable which takes a 1-character string and returns a grid
        item. This is called with each non-ignored character in
        `raw_grid` as argument, and its return value will populate the
        grid at its corresponding location.
    ignore_chars : iterable of str, optional
        Characters to ignore when populating the grid.

    Returns
    -------
    dict of {GridPoint : item}
        Grid created from string lines.
    """
    result: Grid[Item] = {}
    ignore = set(ignore_chars)
    for row, line in enumerate(raw_grid):
        for col, char in enumerate(line):
            if char in ignore:
                continue
            result[row, col] = item_factory(char)
    return result


def interior_area(points: list[GridPoint]) -> float:
    """
    Return the interior area of a simple polygon with grid points as its
    vertices.

    The polygon must not intersect itself, and must not have any holes.
    Its points must be provided in a clockwise or counterclockwise
    order.

    Parameters
    ----------
    points : list of GridPoint
        Vertices of the polygon.

    Returns
    -------
    float
        Area of the polygon.
    """
    # NOTE The "shoelace formula" requires a circular list of vertices.
    padded_points = [*points, points[0]]
    return abs(sum(
        row1 * col2 - row2 * col1
        for (row1, col1), (row2, col2) in pairwise(padded_points)
    )) / 2


type Rotation = Literal["CCW", "CW"]


class Direction(IntEnum):
    """
    Direction enumeration.

    - **UP**: 0
    - **RIGHT**: 1
    - **DOWN**: 2
    - **LEFT**: 3
    """
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def rotate(self, towards: Rotation) -> "Direction":
        """
        Rotate a direction by 90 degrees.

        Parameters
        ----------
        facing :
            Initial direction.
        towards : {'CCW', 'CW'}
            Rotation to apply (`CCW` for counterclockwise, `CW` for
            clockwise).

        Returns
        -------
        Direction
            Rotated direction.
        """
        offset = 1 if towards == "CW" else -1
        return Direction((self.value + offset) % 4)

    @property
    def offset(self) -> GridPoint:
        """
        The `GridPoint` representing this direction.
        """
        return _ROW_COLUMN_OFFSETS[self]


_ROW_COLUMN_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}


class Position(NamedTuple):
    """
    Position representing a grid point and a facing direction.
    """
    point: GridPoint
    facing: Direction

    @property
    def next_point(self) -> GridPoint:
        """
        Return the next point after advancing one step in the current
        direction.

        Returns
        -------
        GridPoint
            Next point in this direction.

        See Also
        --------
        step : Return the next position, instead of the next grid point.
        """
        return add_points(self.point, self.facing.offset)

    def step(self) -> Self:
        """
        Return the next position after advancing one step in the current
        direction.

        Returns
        -------
        Position
            Next position in this direction.

        See Also
        --------
        next_point : Return the next grid point, instead of the next
            position.
        """
        return type(self)(self.next_point, self.facing)

    def rotate(self, towards: Rotation) -> Self:
        """
        Rotate the facing direction by 90 degrees.

        Parameters
        ----------
        towards : {'CCW', 'CW'}
            Rotation to apply (`CCW` for counterclockwise, `CW` for
            clockwise).

        Returns
        -------
        Position
            Rotated position.
        """
        return type(self)(self.point, self.facing.rotate(towards))


__all__ = [
    "Direction",
    "Grid",
    "GridPoint",
    "Position",
    "Rotation",
    "add_points",
    "neighbors",
    "parse_grid",
    "interior_area",
    "subtract_points",
    "taxicab_distance",
]
