from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS
import cProfile
from collections.abc import Callable
from contextlib import redirect_stdout
from importlib import import_module
import os
from pathlib import Path
from time import perf_counter_ns
import timeit
from traceback import print_exc
from typing import Any, SupportsIndex, Type, cast

from solutions.base import AocException, BaseSolution


def nanoseconds_str(ns: float) -> str:
    """
    Format a number of nanoseconds into a human-readable string.

    Parameters
    ----------
    ns : float
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
    description="Run Josiah Winslow's Advent of Code solutions.",
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
    "-t", "--test", help=(
        "run using test input(s) instead of the day's actual input"
    ),
    action="store_true",
)
PARSER.add_argument(
    "--debug", help="print debug statements",
    action="store_true",
)
PARSER.add_argument(
    "-b", "--benchmark", help=(
        "times to run solution for benchmarking (default 100; if left "
        "out, solution is not benchmarked)"
    ),
    metavar="RUNS",
    nargs="?",
    type=int, default=SUPPRESS,
)
PARSER.add_argument(
    "-s", "--slow", help=(
        "specify that long-running solutions should be run"
    ),
    action="store_true",
)
PARSER.add_argument(
    "-p", "--profile", help="profile solution",
    action="store_true",
)


def main(
        year: int,
        day: int,
        slow: bool,
        debug: bool,
        test: bool,
        benchmark: int,
):
    # Import solution module
    try:
        solution_module = import_module(
            f"solutions.{year}.day{day:02}.solution"
        )
    except ModuleNotFoundError as e:
        raise AocException(
            f"solution module not found for {year} day {day}"
        ) from e

    # Initialize solution class
    try:
        solution_class = cast(
            Type[BaseSolution[Any]],
            getattr(solution_module, "Solution"),
        )
    except AttributeError as e:
        raise AocException(
            f"solution class not found for {year} day {day}"
        ) from e
    solution = solution_class(
        run_if_slow=slow,
        testing=test,
        debugging=debug,
    )

    # Find input file / test files
    assert solution_module.__file__ is not None
    solution_path = Path(solution_module.__file__).parent
    INPUT_FILE = "input.txt"
    if test:
        files = [
            file
            for file in solution_path.iterdir()
            if file.is_file()
            and file.suffix == ".txt"
            and file.name != INPUT_FILE
        ]
    else:
        files = [solution_path / INPUT_FILE]

    # Run solution on each input / test file
    for file in files:
        print(f"# {file.relative_to(solution_path.parent.parent)}")
        print()
        solution.read_input_file(file)

        if benchmark > 0:
            benchmark_solution(solution, benchmark)
            print()
            continue

        try:
            solution.run_and_print_solutions()
        except AocException:
            raise
        except Exception:
            print_exc()


def benchmark_solution(solution: BaseSolution[Any], benchmark: int):
    print("## Benchmarking results")

    parts_are_separated = type(solution).solve is BaseSolution[Any].solve
    # Warn about not benchmarking slow functions
    slow_functions: set[str] = set()
    if not solution.run_if_slow:
        for func in (
            (solution.part_1, solution.part_2)
            if parts_are_separated
            else (solution.solve,)
        ):
            func_is_slow = getattr(func, "_slow", False)
            if func_is_slow:
                print(f"Not benchmarking slow function: {func.__name__}")
                slow_functions.add(func.__name__)

    # Prepare solution function
    run_solution = solution.solve
    # HACK If functions wrapped by functools.lru_cache are used in the
    # solution, the benchmark should clear their caches before running
    # the solution for a more accurate benchmark.
    clear_cache_functions: list[Callable[[], None]] = [
        clear_cache_func
        for func in getattr(solution, "_cached_functions", [])
        if (clear_cache_func := getattr(func, "cache_clear", None))
    ]
    if clear_cache_functions:
        def run_solution_with_clear_cache():
            for func in clear_cache_functions:
                func()
            return solution.solve()
        run_solution = run_solution_with_clear_cache

    # Time solution function
    timer = timeit.Timer(run_solution, timer=perf_counter_ns)
    try:
        # HACK Nothing should be printed while benchmarking; to ensure
        # this, we use context managers to redirect STDOUT to the "null
        # device".
        with open(os.devnull, "w") as fnull:
            with redirect_stdout(fnull):
                solution_time = timer.timeit(number=benchmark)
    except AocException:
        raise
    except Exception:
        timer.print_exc()
        return

    # Print benchmarking results
    if "solve" in slow_functions:
        what = "Solution was skipped"
    elif {"part_1", "part_2"} <= slow_functions:
        what = "Both parts were skipped"
    elif "part_1" in slow_functions:
        what = "Part 2 ran"
    elif "part_2" in slow_functions:
        what = "Part 1 ran"
    else:
        what = "Both parts ran" if parts_are_separated else "Solution ran"
    print(f"{what} {benchmark} time{"" if benchmark == 1 else "s"}.")
    print(f"-   Total: {nanoseconds_str(solution_time)}")
    print(f"- Per run: {nanoseconds_str(solution_time / benchmark)}")


if __name__ == "__main__":
    ARGS = PARSER.parse_args()

    if ARGS.profile:
        cProfile.run(
            "main(ARGS.year, ARGS.day, ARGS.slow, ARGS.debug, ARGS.test, 0)",
            sort="tottime",
        )
    else:
        # Determine the number of times to run for benchmarking
        if not hasattr(ARGS, "benchmark"):
            benchmark = 0
        elif ARGS.benchmark is None:
            benchmark = 100
        else:
            benchmark = ARGS.benchmark

        main(ARGS.year, ARGS.day, ARGS.slow, ARGS.debug, ARGS.test, benchmark)
