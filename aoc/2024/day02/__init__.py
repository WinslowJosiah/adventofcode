from collections.abc import Iterable
import itertools as it


def check_report_safety(report: Iterable[int]) -> bool:
    """
    Check whether a given report is safe if no levels are removed.
    """
    diffs = [b - a for a, b in it.pairwise(report)]
    return (
        # For increasing reports
        all(1 <= d <= 3 for d in diffs)
        # For decreasing reports
        or all(-3 <= d <= -1 for d in diffs)
    )


def aoc2024_day02_part1(lines: Iterable[str]) -> int:
    safe_reports = 0
    for line in lines:
        report = list(map(int, line.split()))
        if check_report_safety(report):
            safe_reports += 1

    return safe_reports


def aoc2024_day02_part2(lines: Iterable[str]) -> int:
    safe_reports = 0
    for line in lines:
        report = list(map(int, line.split()))
        if (
            # If the report itself is safe...
            check_report_safety(report)
            # ...or any version of it with one level removed is safe
            or any(
                check_report_safety(report[:i] + report[i + 1:])
                for i in range(len(report))
            )
        ):
            safe_reports += 1

    return safe_reports


parts = (aoc2024_day02_part1, aoc2024_day02_part2)
