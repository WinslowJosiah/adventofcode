from collections.abc import Callable
from enum import Enum, auto
from functools import wraps
import inspect
from pprint import pprint
from typing import (
    Any, TYPE_CHECKING, TypeVar, cast, final, get_origin, overload,
)

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath


class AocException(Exception):
    """
    Custom exception class for issues related to creating/running
    solutions.
    """


class InputTypes(Enum):
    # one single block of text
    TEXT = auto()
    # one single integer
    INTEGER = auto()
    # a list of strings, split by a separator (default newline)
    STRSPLIT = auto()
    # a list of ints, split by a separator (default newline)
    INTSPLIT = auto()


type InputType = str | int | list[str] | list[int]
type ResultType = int | str | None


def print_answer(part: int, answer: ResultType):
    """
    Print a formatted version of the answer.

    Parameters
    ----------
    part : int
        Part number.
    answer : ResultType
        Result.
    """
    if answer is None:
        return
    print(f"### Part {part}")
    print(answer)


class BaseSolution[I: InputType]:
    separator = "\n"

    # NOTE These attributes are defined by subclasses.
    input_type: InputTypes = InputTypes.TEXT
    _year: int
    _day: int
    # HACK This will contain any cached functions used in the solution,
    # so that the function that benchmarks them can clear their caches
    # on every run.
    _cached_functions: tuple[Callable[..., Any], ...] | None

    def __init__(
            self,
            run_if_slow: bool = False,
            testing: bool = False,
            debugging: bool = False,
    ):
        self.run_if_slow = run_if_slow
        self.testing = testing
        self.debugging = debugging

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}<year={self.year}, day={self.day}>("
            + ", ".join(
                f"{name}={attr!r}"
                for name in ("run_if_slow", "testing", "debugging")
                if (attr := getattr(self, name))
            )
            + ")"
        )

    @final
    @property
    def year(self) -> int:
        if not hasattr(self, "_year"):
            raise NotImplementedError("Solution._year not defined")
        return self._year

    @final
    @property
    def day(self) -> int:
        if not hasattr(self, "_day"):
            raise NotImplementedError("Solution._day not defined")
        return self._day

    def solve(self) -> tuple[ResultType, ResultType]:
        """
        Return the answers to Parts 1 and 2 of the Advent of Code
        puzzle.

        Returns
        -------
        tuple of (ResultType, ResultType)
            The Part 1 solution and the Part 2 solution.
        """
        return self.part_1(), self.part_2()

    def part_1(self) -> ResultType:
        """
        Return the answer to Part 1 of the Advent of Code puzzle.

        Use this function only if a unified `solve()` function is not
        implemented.

        Returns
        -------
        ResultType
            The Part 1 solution.
        """
        raise NotImplementedError

    def part_2(self) -> ResultType:
        """
        Return the answer to Part 2 of the Advent of Code puzzle.

        Use this function only if a unified `solve()` function is not
        implemented.

        This function is not needed on the last day of the year (Day 25
        for years <=2024, Day 12 for all other years).

        Returns
        -------
        ResultType
            The Part 2 solution.
        """
        if self.day != (25 if self.year <= 2024 else 12):
            raise NotImplementedError

    @final
    def read_input_file(self, inp: "FileDescriptorOrPath"):
        """
        Read input from a file.

        The contents of the file will be used to provide input to the
        solution methods.

        Parameters
        ----------
        inp : file descriptor or path
            File to read from.
        """
        with open(inp) as f:
            self.read_input_str(f.read())

    @final
    def read_input_str(self, st: str) -> InputType:
        """
        Read input from a string.

        The contents of the string will be used to provide input to the
        solution methods.

        Parameters
        ----------
        st : str
            String to read from.

        Returns
        -------
        InputType
            Input that was read.
        """
        result = self._read_input_str(st)
        self.input = cast(I, result)
        return result

    @final
    def _read_input_str(self, st: str) -> InputType:
        data = st.strip("\n")
        if not data:
            raise AocException("input data is empty")
        match self.input_type:
            case InputTypes.TEXT:
                return data
            case InputTypes.INTEGER:
                return int(data)
            case InputTypes.STRSPLIT:
                return data.split(self.separator)
            case InputTypes.INTSPLIT:
                return [int(p) for p in data.split(self.separator)]
            case _:
                raise ValueError(f"Unrecognized input type: {self.input_type}")

    @final
    def run_and_print_solutions(self):
        print(f"## Solutions for Advent of Code {self.year} Day {self.day}")

        result = self.solve()
        try:
            if result:
                for part, answer in enumerate(result, start=1):
                    print_answer(part, answer)
        except TypeError as e:
            raise ValueError(
                f"unable to unpack answers from solve(), got {result!r}"
            ) from e

    @final
    def debug(
            self,
            *objects: Any,
            trailing_newline : bool = False,
            pretty: bool = False,
    ):
        """
        Print any number of objects.

        This is useful as a debugging measure. If `self.debugging` is
        false, nothing will be printed.

        Parameters
        ----------
        *objects
            These objects will be printed.
        trailing_newline : bool, default False
            If true, print a trailing newline.
        pretty : bool, default False
            If true, pretty-print the objects.
        """
        if not self.debugging:
            return
        if pretty:
            for o in objects:
                pprint(o)
        else:
            print(*objects)
        if trailing_newline:
            print()


class TextSolution(BaseSolution[str]):
    """
    Input is of the type `str`.
    """
    input_type = InputTypes.TEXT


class IntSolution(BaseSolution[int]):
    """
    Input is of the type `int`.
    """
    input_type = InputTypes.INTEGER


class StrSplitSolution(BaseSolution[list[str]]):
    """
    Input is of the type `list[str]`, split by a separator (default
    newline); specify `self.separator` to use a different separator.
    """
    input_type = InputTypes.STRSPLIT


class IntSplitSolution(BaseSolution[list[int]]):
    """
    Input is of the type `list[int]`, split by a separator (default
    newline); specify `self.separator` to use a different separator.
    """
    input_type = InputTypes.INTSPLIT


R1 = TypeVar("R1", bound=ResultType)
R2 = TypeVar("R2", bound=ResultType)
S = TypeVar("S", bound=BaseSolution[Any])


@overload
def slow(func: Callable[[S], R1]) -> Callable[[S], R1 | None]: ...
@overload
def slow(
        func: Callable[[S], tuple[R1, R2]],
) -> Callable[[S], tuple[R1 | None, R2 | None]]: ...
def slow(
        func: Callable[[S], R1 | tuple[R1, R2]],
) -> Callable[[S], R1 | None | tuple[R1 | None, R2 | None]]:
    """
    Decorator to mark a solution method as "slow".

    If `self.run_if_slow` is false, methods with this decorator will not
    be run.
    """
    @wraps(func)
    def wrapper(self: S) -> R1 | None | tuple[R1 | None, R2 | None]:
        if self.run_if_slow:
            return func(self)
        print(f"Not running slow function: {func.__name__}")

        # HACK There is no easy way to type-check the result of a
        # function without running it. So to make solve() return two
        # results when wrapped, its name is checked for explicitly.
        if func.__name__ == "solve":
            return (None, None)
        # HACK If that check doesn't work somehow, we could check the
        # return type annotation (if any). If it's annotated as a tuple,
        # it's probably the solve function in disguise.
        sig = inspect.signature(func)
        if sig.return_annotation != inspect.Signature.empty:
            origin = get_origin(sig.return_annotation)
            if origin is tuple:
                return (None, None)

        return None

    # HACK The _slow attribute of the slow function is set to true.
    setattr(wrapper, "_slow", True)
    return wrapper


E = TypeVar("E", ResultType, tuple[ResultType, ResultType])


def answer(expected: E) -> Callable[[Callable[[S], E]], Callable[[S], E]]:
    """
    Decorator to assert that the result of the solution method is a
    certain value.

    If the result does not match the expected value, an exception is
    raised. This check will not happen if `self.testing` is true (i.e.
    if using testing data), or if the method is marked as "slow" and
    does not run.

    Parameters
    ----------
    expected : ResultType or tuple of (ResultType, ResultType)
        Expected value of method.

    Returns
    -------
    decorator
        Decorator that checks the result of the method against the
        expected value.
    """
    def deco(func: Callable[[S], E]) -> Callable[[S], E]:
        @wraps(func)
        def wrapper(self: S) -> E:
            result = func(self)
            if (
                self.testing
                or result is None
                or result == (None, None)
                or result == expected
            ):
                return result
            raise AocException(
                "Failed @answer assertion for "
                f"year {self.year} day {self.day} ({func.__name__})\n"
                f"returned: {result}\texpected: {expected}"
            )
        return wrapper
    return deco
