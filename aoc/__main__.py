from argparse import ArgumentParser, SUPPRESS
from collections.abc import Callable, Iterable, Iterator
import pathlib
import sys
import time
import timeit
import traceback
from typing import Any


FILE_PATH = pathlib.Path(__file__).parent


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


def main(year: int, day: int, times_to_run: int, input_paths: list[str] | None):
    module_path = FILE_PATH.joinpath(f"{year}").joinpath(f"day{day:0>2}")

    # Import parts tuple from the module for this year/day
    # NOTE: parts should be a tuple with two functions, both taking an
    # iterable of strings (the lines of the input file).
    try:
        parts: tuple[Callable[[Iterable[str]], Any]] = getattr(
            __import__(
                f"{year}.day{day:0>2}",
                globals=globals(),
                locals=locals(),
                fromlist=("parts",),
            ),
            "parts"
        )
    except ModuleNotFoundError:
        print("error: could not find code!")
        return

    paths_to_check: Iterable[pathlib.Path]
    # If input paths were provided
    if input_paths is not None:
        # We will check the provided paths
        paths_to_check = []
        for p in input_paths:
            path_to_check = pathlib.Path(p)
            paths_to_check.append(
                path_to_check
                if path_to_check.is_absolute()
                else module_path.joinpath(path_to_check)
            )
    else:
        # Otherwise, we will check all .txt files stored near the code
        paths_to_check = module_path.glob("**/*.txt")

    # Look for files to use as input
    file_paths = sorted(
        file_path
        for file_path in paths_to_check
        if file_path.is_file()
    )
    if not file_paths:
        print("error: no input files!")
        return

    # The .txt files will each be used as inputs
    for file_path in file_paths:
        try:
            pretty_file_path = file_path.relative_to(module_path)
        except ValueError:
            pretty_file_path = file_path
        print("Input file:", pretty_file_path)

        print()
        print("Return values")
        # Run both parts normally
        for part in parts:
            print(f"{part.__name__}: ", end="", flush=True)

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
        # Skip benchmarking if not benchmarking
        if times_to_run <= 0:
            continue

        print(f"Time for {times_to_run} runs")
        # Run both parts many times, and time them with timeit
        for part in parts:
            print(f"{part.__name__}: ", end="", flush=True)

            def func_to_time():
                with file_path.open() as f:
                    part(readlines_strip_linefeed(f))

            timer = timeit.Timer(
                func_to_time,
                timer=time.perf_counter_ns,  # More accurate timer!
                globals=globals(),
            )
            try:
                part_time = timer.timeit(number=times_to_run)
            except Exception:
                print()
                print()
                timer.print_exc()
                print()
                continue

            print(
                nanoseconds_str(part_time),
                f"({nanoseconds_str(part_time / times_to_run)} per run)"
            )

        print()


if __name__ == "__main__":
    # We expect the relevant info to be typed into the command line, so
    # we'll use argparse to parse the args (self-explanatory)
    parser = ArgumentParser(
        description="Run Josiah Winslow's Advent of Code solutions.",
    )
    parser.add_argument(
        "-y", "--year", help="year number", metavar="YYYY",
        type=int, required=True,
    )
    parser.add_argument(
        "-d", "--day", help="day number", metavar="D",
        type=int, required=True,
    )
    parser.add_argument(
        "-b", "--benchmark", help=(
            "times to run day's solution for benchmarking (default "
            "100; if left out, solution is not benchmarked)"
        ),
        metavar="RUNS",
        nargs="?",
        type=int, default=SUPPRESS,
    )
    parser.add_argument(
        "-i", "--input", help=(
            "paths to input files relative to day directory (if left "
            "out, uses all .txt files in code directory)"
        ),
        metavar="FILE",
        nargs="+",
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

    # Figure out how many times to run for benchmarking
    times_to_run = 0
    if "benchmark" in args:
        if args.benchmark is not None:
            times_to_run = args.benchmark
        else:
            times_to_run = 100

    # Use the arguments in the main function (finally!)
    main(
        year=args.year,
        day=args.day,
        times_to_run=times_to_run,
        input_paths=args.input,
    )
