from argparse import ArgumentParser, ArgumentTypeError
from collections.abc import Callable
from pathlib import Path
from typing import SupportsIndex


def ranged_int(
        start: SupportsIndex,
        stop: SupportsIndex,
) -> Callable[[str], int]:
    """
    Use as an argparse type to restrict an integer to a specific
    (inclusive) range.

    Parameters
    ----------
    start : int
        Inclusive start of range.
    stop : int
        Inclusive end of range.

    Returns
    -------
    callable
        Function that checks whether a string is an integer within the
        specified range.

    Notes
    -----
    When used as an argparse type, an `argparse.ArgumentTypeError` is
    raised if the value is not convertible to an integer, or the value
    is not within the inclusive range from `start` to `stop`.
    """
    def checker(s: str) -> int:
        try:
            value = int(s)
        except ValueError:
            raise ArgumentTypeError("value not an integer")
        if int(start) <= value <= int(stop):
            return value
        raise ArgumentTypeError(f"value not in range [{start}, {stop}]")
    return checker


PARSER = ArgumentParser(
    description="Initialize Josiah Winslow's Advent of Code solutions.",
)
PARSER.add_argument(
    "-y", "--year", help="year number", metavar="YYYY",
    type=int, required=True,
)
PARSER.add_argument(
    "-d", "--day", help="day number (1-25)", metavar="D",
    type=ranged_int(1, 25), required=True,
)


def main(year: int, day: int):
    FILE_DIR = Path(__file__).parent

    # Create year and day directories
    year_dir = Path(FILE_DIR, "solutions", str(year))
    year_dir.mkdir(parents=True, exist_ok=True)
    day_dir = Path(year_dir, f"day{day:02}")
    day_dir.mkdir(parents=True, exist_ok=True)

    # Create input and test files
    Path(day_dir, "input.txt").touch()
    Path(day_dir, "test.txt").touch()

    # Create solution file
    solution_path = Path(day_dir, "solution.py")
    if solution_path.exists():
        print("solution file exists")
    else:
        template = Path(FILE_DIR, "solution.py.tmpl").read_text()
        replaced_template = (
            template.replace("{{year}}", str(year))
            .replace("{{day}}", str(day))
        )
        solution_path.write_text(replaced_template)

    print(f"AoC {year} Day {day} initialized at: {day_dir}")


if __name__ == "__main__":
    ARGS = PARSER.parse_args()

    main(ARGS.year, ARGS.day)
