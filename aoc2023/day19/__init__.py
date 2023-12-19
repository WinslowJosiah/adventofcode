from collections.abc import Iterable
from enum import Enum
from itertools import takewhile
import re
from typing import NamedTuple


# This regex matches a workflow, and groups its name and rule string
workflow_regex = re.compile(r"([a-z]+){(.+?)}")
# This regex matches a rule, and groups each part of its condition and
# destination 
rule_regex = re.compile(r"(?:([amsx])([<>])(\d+):)?([a-z]+|A|R)")
# This regex matches a part, and groups the inside of the part string
part_regex = re.compile(r"{(.+?)}")


class Operator(Enum):
    LESS_THAN = "<"
    GREATER_THAN = ">"


class Condition(NamedTuple):
    category: str
    op: Operator
    value: int


class Rule(NamedTuple):
    condition: Condition | None
    destination: str


def create_workflows(lines: Iterable[str]) -> dict[str, list[Rule]]:
    """
    Create a collection of workflows from each line in `lines`. Each
    workflow will have a name and a list of rules to apply.
    """
    workflows: dict[str, list[Rule]] = {}
    # For each line in the input
    for line in lines:
        # Extract the name and list of rules for this workflow
        re_match = workflow_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        name, rules_str = re_match.groups()

        rules: list[Rule] = []
        # For each comma-separated rule
        for rule_str in rules_str.split(","):
            # Extract the properties of the rule
            re_match = rule_regex.fullmatch(rule_str)
            # This makes the type checker happy
            assert re_match is not None
            category, op, value, destination = re_match.groups()

            # If a category has been specified
            if category is not None:
                # There exists a condition
                condition = Condition(
                    category=category,
                    op=Operator(op),
                    value=int(value),
                )
            else:
                # Otherwise, there exists no condition
                condition = None

            # Construct the rule using our condition and destination
            rules.append(Rule(condition, destination))
        # We now have the name and rules of a workflow
        workflows[name] = rules

    return workflows


def aoc2023_day19_part1(lines: Iterable[str]) -> int:
    line_iter = iter(lines)
    workflows = create_workflows(
        # The input defines workflows up until the first blank line
        takewhile(lambda line: line, line_iter)
    )
    # NOTE: After defining the workflows, the input defines parts until
    # the end of the file.

    parts: list[dict[str, int]] = []
    # For each remaining line in the input
    for line in line_iter:
        # Extract the part's category definitions
        re_match = part_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        categories_str, = re_match.groups()

        part: dict[str, int] = {}
        # For each comma-separated category definition
        for category_str in categories_str.split(","):
            # The category name and value are separated by =
            category, value = category_str.split("=")
            part[category] = int(value)
        # This is a part
        parts.append(part)

    rating_sum = 0
    # For each part we have to process
    for part in parts:
        workflow = "in"
        # Until this part is accepted or rejected
        while workflow not in ("A", "R"):
            # We must apply each rule in the current workflow
            for rule in workflows[workflow]:
                condition, destination = rule
                # If there is no condition
                if condition is None:
                    # Go automatically to the destination
                    workflow = destination
                    break

                category_value = part[condition.category]
                # Check whether this rule applies
                match condition.op:
                    case Operator.LESS_THAN:
                        rule_applies = category_value < condition.value
                    case Operator.GREATER_THAN:
                        rule_applies = category_value > condition.value

                # If this rule does apply, go to the destination
                if rule_applies:
                    workflow = destination
                    break

        # If this part has been accepted
        if workflow == "A":
            # Add its ratings to the running total
            rating_sum += sum(part.values())

    return rating_sum


def aoc2023_day19_part2(lines: Iterable[str]) -> int:
    from collections import deque
    from math import prod

    line_iter = iter(lines)
    workflows = create_workflows(
        # The input defines workflows up until the first blank line
        takewhile(lambda line: line, line_iter)
    )
    # NOTE: For this task, we can skip processing the parts.

    combos = 0
    # Each category can be in the range of 1 to 4000 inclusive
    workflow_ranges: deque[tuple[str, dict[str, range]]] = deque([
        ("in", {category: range(1, 4001) for category in "xmas"}),
    ])
    # While there are ranges left to process
    while workflow_ranges:
        workflow, part = workflow_ranges.popleft()
        # If these ranges are accepted
        if workflow == "A":
            # Add these possibilities to the number of accepted combos
            combos += prod(map(len, part.values()))
            continue
        # If these ranges are rejected
        elif workflow == "R":
            # Do nothing
            continue

        # Apply each rule in the current workflow
        for rule in workflows[workflow]:
            condition, destination = rule
            # If there is no condition
            if condition is None:
                # These combos go automatically to the destination
                workflow_ranges.append((destination, part))
                continue

            category, op, value = condition
            # The condition will split this range into two ranges...
            category_range = part[category]
            # ...one that doesn't match the condition (and has the next
            # rule in this workflow applied to it)...
            start, stop = category_range.start, category_range.stop
            # ...and one that does match the condition (and moves on to
            # the destination workflow)
            new_start, new_stop = start, stop

            # Split the range
            match op:
                case Operator.LESS_THAN:
                    start = max(start, value)
                    new_stop = min(new_stop, value)
                case Operator.GREATER_THAN:
                    new_start = max(new_start, value + 1)
                    stop = min(stop, value + 1)

            # The matching range goes to the destination
            workflow_ranges.append(
                (destination, part | {category: range(new_start, new_stop)})
            )
            # The non-matching range stays here, to have future rules
            # applied to it
            part[category] = range(start, stop)

    return combos


parts = (aoc2023_day19_part1, aoc2023_day19_part2)
