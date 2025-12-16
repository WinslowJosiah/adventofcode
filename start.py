from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
import urllib.request

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
PARSER.add_argument(
    "-i", "--input", help="get puzzle input from adventofcode.com",
    action="store_true",
)


def wait_until_unlock(year: int, day: int) -> bool:
    # AoC unlocks at midnight EST (UTC-5)
    unlock_time = datetime(year, 12, day, 5, 0, 0, tzinfo=timezone.utc)

    while True:
        now = datetime.now(timezone.utc)
        if now >= unlock_time:
            break

        seconds_remaining = round((unlock_time - now).total_seconds())

        if seconds_remaining > 60 * 60:
            print("Puzzle unlocking in over an hour; not waiting.")
            return False
        elif seconds_remaining > 60:
            print(
                f"Puzzle unlocking in {seconds_remaining // 60} "
                "minute(s)..."
            )
        else:
            print(
                f"Puzzle unlocking in {seconds_remaining} second(s)..."
            )

        sleep(1 if seconds_remaining < 60 else 10)

    print("Puzzle unlocked!")
    return True


def fetch_input(year: int, day: int, session_cookie: str) -> str:
    url = f"https://adventofcode.com/{year}/day/{day}/input"
    req = urllib.request.Request(
        url,
        headers={
            "Cookie": f"session={session_cookie}",
            "User-Agent": (
                "https://github.com/WinslowJosiah/adventofcode/blob"
                "/main/start.py by Josiah Winslow "
                "(winslowjosiah@gmail.com)"
            ),
        },
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")


def main(year: int, day: int, input: bool):
    FILE_DIR = Path(__file__).parent

    # Create year and day directories
    year_dir = Path(FILE_DIR, "solutions", str(year))
    year_dir.mkdir(parents=True, exist_ok=True)
    day_dir = Path(year_dir, f"day{day:02}")
    day_dir.mkdir(parents=True, exist_ok=True)

    # Create input and test files
    input_path = Path(day_dir, "input.txt")
    input_path.touch()
    # NOTE If any test files already exist, we won't create a new one.
    if not any(day_dir.glob("test*.txt")):
        Path(day_dir, "test.txt").touch()

    # Create solution file
    solution_path = Path(day_dir, "solution.py")
    # Populate solution file using template if it doesn't exist
    if not solution_path.exists():
        template = Path(FILE_DIR, "solution.py.tmpl").read_text()
        replaced_template = (
            template.replace("{{year}}", str(year))
            .replace("{{day}}", str(day))
        )
        solution_path.write_text(replaced_template)

    print(f"AoC {year} Day {day} initialized at: {day_dir}")

    # Stop here if input file wasn't requested or it is nonempty
    if not input:
        print("Not populating input.txt.")
        return
    if input_path.stat().st_size != 0:
        print("input.txt exists and is populated.")
        return
    print("Populating input.txt...")

    # Obtain session cookie from config file
    config = ConfigParser()
    if not config.read("config.ini"):
        print("config.ini not found; please create it.")
        return
    session_cookie = config.get("aoc", "session", fallback=None)
    if session_cookie is None:
        print("Session cookie is not set; please set it in config.ini.")
        return

    # Fetch puzzle input and populate input file
    if not wait_until_unlock(year, day):
        return
    input_text = fetch_input(year, day, session_cookie)
    input_path.write_text(input_text)
    print("input.txt populated with puzzle input.")


if __name__ == "__main__":
    ARGS = PARSER.parse_args()

    main(ARGS.year, ARGS.day, ARGS.input)
