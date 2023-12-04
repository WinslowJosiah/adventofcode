from argparse import ArgumentParser
from collections.abc import Callable, Iterable, Iterator
import pathlib
import sys
import time
import timeit
import traceback
from typing import Any


FILE_PATH = pathlib.Path(__file__).parent
# Number of times to run for timeit
NUMBER_OF_RUNS = 1000


def readlines_strip_linefeed(f: Iterable[str]) -> Iterator[str]:
    """
    Read from a file (or iterable) line by line with the `\\n`
    character right-stripped from each line.

    Parameters
    ----------
    f : iterable of str
        File (or iterable) to read from.

    Yields
    ------
    str
        Line from `f` without an ending linefeed.
    """
    for line in f:
        yield line.rstrip("\n")

def nanoseconds_str(ns: int | float) -> str:
    """
    Format a number of nanoseconds into a human-readable string.

    Parameters
    ----------
    ns : int or float
        Number of nanoseconds.

    Returns
    -------
    str
        Human-readable string representation of nanoseconds.
    """
    if ns < 1e3:
        return f"{ns} ns"
    if ns < 1e6:
        return f"{ns / 1e3:.3f} μs"
    if ns < 1e9:
        return f"{ns / 1e6:.3f} ms"

    return f"{ns / 1e9:.3f} s"


def main(year: int, day: int):
    module_path = FILE_PATH.joinpath(f"aoc{year}").joinpath(f"day{day:0>2}")

    # Import parts tuple from the module for this year/day
    # NOTE: parts should be a tuple with two functions, both taking an
    # iterable of strings (the lines of the input file).
    try:
        parts: tuple[Callable[[Iterable[str]], Any]] = getattr(
            __import__(
                f"aoc{year}.day{day:0>2}",
                globals=globals(),
                locals=locals(),
                fromlist=("parts",),
            ),
            "parts"
        )
    except ModuleNotFoundError:
        print("error: could not find code!")
        return

    # Look for all .txt files stored near the code
    file_paths = sorted(
        file_path
        for file_path in module_path.glob("**/*.txt")
        # NOTE: Sometimes paths ending in .txt are folders.
        # Don't ask me why.
        if file_path.is_file()
    )
    if not file_paths:
        print("error: no input files!")
        return

    # The .txt files will each be used as inputs
    for file_path in file_paths:
        print("Input file:", file_path.relative_to(module_path))

        print()
        print("Return values")
        # Run both parts normally
        for part in parts:
            print(f"{part.__name__}: ", end="")

            with file_path.open() as f:
                try:
                    return_value = part(readlines_strip_linefeed(f))
                except Exception:
                    print()
                    print()
                    traceback.print_exc()
                    print()
                    continue

                print(return_value)

        print()
        print(f"Time for {NUMBER_OF_RUNS} runs")
        # Run both parts many times, and time them with timeit
        for part in parts:
            print(f"{part.__name__}: ", end="")

            def func_to_time():
                with file_path.open() as f:
                    part(readlines_strip_linefeed(f))

            timer = timeit.Timer(
                func_to_time,
                timer=time.perf_counter_ns,  # More accurate timer!
                globals=globals(),
            )
            try:
                part_time = timer.timeit(number=NUMBER_OF_RUNS)
            except Exception:
                print()
                print()
                timer.print_exc()
                print()
                continue

            print(
                nanoseconds_str(part_time),
                f"({nanoseconds_str(part_time / NUMBER_OF_RUNS)} per run)"
            )

        print()


if __name__ == "__main__":
    # We expect the relevant info to be typed into the command line, so
    # we'll use argparse to parse the args (self-explanatory)
    parser = ArgumentParser(
        description="Run Josiah Winslow's Advent of Code solutions.",
    )
    parser.add_argument(
        "--year", "-y", help="year number", metavar="YYYY",
        type=int, required=True,
    )
    parser.add_argument(
        "--day", "-d", help="day number", metavar="D",
        type=int, required=True,
    )

    # If there aren't any arguments to parse
    if len(sys.argv) < 2:
        # Print help message and exit with error
        parser.print_help()
        sys.exit(1)

    # Overwrite the error handler to also print a help message
    # HACK: This is what's known in the biz as a "monkey-patch". Don't
    # worry if it doesn't make sense to you; it makes sense to argparse,
    # and that's all that matters.
    def custom_error_handler(_self: ArgumentParser):
        def wrapper(message: str):
            sys.stderr.write(f"{_self.prog}: error: {message}\n")
            _self.print_help()
            sys.exit(2)
        return wrapper
    parser.error = custom_error_handler(parser)

    # Parse the given arguments
    args = parser.parse_args()
    # Use the arguments in the main function (finally!)
    main(**vars(args))
