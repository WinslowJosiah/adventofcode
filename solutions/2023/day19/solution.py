# https://adventofcode.com/2023/day/19

from collections.abc import Callable
from math import prod
from operator import gt, lt
import re

from ...base import StrSplitSolution, answer


type Part = dict[str, int]
type Filter = Callable[[Part], str]
type RangedPart = dict[str, range]
type RangedFilter = Callable[[RangedPart], list[tuple[str, RangedPart]]]


def parse_part(raw_part: str) -> Part:
    return {k: int(v) for k, v in re.findall(r"(.)=(\d+)", raw_part)}


def parse_workflow[F](
        raw_workflow: str,
        builder: Callable[[str, str], F],
) -> tuple[str, F]:
    if not (match := re.search(r"(.*){(.*)}", raw_workflow)):
        raise ValueError(f"could not parse workflow: {raw_workflow}")
    name, raw_filters = match.groups()
    raw_filters, default = raw_filters.rsplit(",", maxsplit=1)
    return name, builder(raw_filters, default)


def parse_filter(
        raw_filter: str
) -> tuple[str, Callable[[int, int], bool], int, str]:
    """
    Parse filter string, and return its category, operator function,
    value, and destination.
    """
    category = raw_filter[0]
    op = gt if raw_filter[1] == ">" else lt
    value_str, destination = raw_filter[2:].split(":")
    return category, op, int(value_str), destination


def build_workflow(raw_filters: str, default: str) -> Filter:
    """
    Create a function that applies filters to a `Part` and returns its
    destination if any (and `default` otherwise).
    """
    def _apply_filters(part: Part) -> str:
        for raw_filter in raw_filters.split(","):
            if not raw_filter:
                continue
            category, op, value, destination = parse_filter(raw_filter)
            if op(part[category], value):
                return destination
        return default

    return _apply_filters


def build_ranged_workflow(raw_filters: str, default: str) -> RangedFilter:
    """
    Create a function that applies filters to a `RangedPart` and returns
    a list of destinations and the `RangedPart`s that reach them.
    """
    def _apply_filters(part: RangedPart) -> list[tuple[str, RangedPart]]:
        ranges: list[tuple[str, RangedPart]] = []
        for raw_filter in raw_filters.split(","):
            if not raw_filter:
                continue
            category, op, value, destination = parse_filter(raw_filter)
            if op == gt:
                unsent, sent = split_range(part[category], value + 1)
            else:
                sent, unsent = split_range(part[category], value)

            ranges.append((destination, {**part, category: sent}))
            part = {**part, category: unsent}

        # The RangedPart that matched no filters gets sent to `default`
        return ranges + [(default, part)]

    return _apply_filters


def split_range(r: range, value: int) -> tuple[range, range]:
    return range(r.start, value), range(value, r.stop)


class Solution(StrSplitSolution):
    """
    Solution for Advent of Code 2023 Day 19.
    """
    _year = 2023
    _day = 19

    separator = "\n\n"

    @answer(398527)
    def part_1(self) -> int:
        workflows_block, parts_block = self.input
        workflows: dict[str, Filter] = dict(
            parse_workflow(line, build_workflow)
            for line in workflows_block.splitlines()
        )

        def score_part(workflow_name: str, part: Part) -> int:
            if workflow_name == "R":
                return 0
            if workflow_name == "A":
                return sum(part.values())
            return score_part(workflows[workflow_name](part), part)

        return sum(
            score_part("in", parse_part(line))
            for line in parts_block.splitlines()
        )

    @answer(133973513090020)
    def part_2(self) -> int:
        workflows_block, _ = self.input
        workflows: dict[str, RangedFilter] = dict(
            parse_workflow(line, build_ranged_workflow)
            for line in workflows_block.splitlines()
        )

        def score_workflow(workflow_name: str, part: RangedPart) -> int:
            if workflow_name == "R":
                return 0
            if workflow_name == "A":
                return prod(len(r) for r in part.values())

            return sum(
                score_workflow(next_name, next_part)
                for next_name, next_part in workflows[workflow_name](part)
            )

        return score_workflow("in", {k: range(1, 4001) for k in "xmas"})
