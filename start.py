from argparse import ArgumentParser
from pathlib import Path

from aoc import ranged_int


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
    # NOTE If any test files already exist, we won't create a new one.
    if not any(day_dir.glob("test*.txt")):
        Path(day_dir, "test.txt").touch()

    # Create solution file
    solution_path = Path(day_dir, "solution.py")
    if solution_path.exists():
        print("Solution file exists; this is probably a rerun.")
        return

    # Populate solution file using template
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
