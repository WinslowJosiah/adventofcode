from collections.abc import Iterable


def aoc2023_day01_part1(lines: Iterable[str]) -> int:
    calibration_sum = 0
    for line in lines:
        # Find first digit in line
        first_digit = next((c for c in line if c.isdigit()), "0")
        # Find last digit in line
        last_digit = next((c for c in reversed(line) if c.isdigit()), "0")
        # Value = first digit concatenated with last digit, as a number
        calibration_value = int(first_digit + last_digit)
        calibration_sum += calibration_value

    return calibration_sum


def aoc2023_day01_part2(lines: Iterable[str]) -> int:
    import re

    digit_dict = {
        "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6",
        "seven": "7", "eight": "8", "nine": "9",
    }
    # This regex will match anything that's followed by a digit, or by
    # one of our 9 number strings
    digit_regex = re.compile(r"(?=(\d|" + "|".join(digit_dict) + r"))")
    # NOTE: re.finditer normally finds all non-overlapping matches.
    # However, we need to find all matches, even if they overlap.
    # "oneight", for example, should result in a last digit of 8, but
    # searching for only non-overlapping matches would result in a last
    # digit of 1.
    # To get around this, we use "positive lookahead" - we search for
    # anything that is immediately followed by our pattern - and put the
    # text in a capturing group so we can retrieve it.

    calibration_sum = 0
    for line in lines:
        digit_iter = digit_regex.finditer(line)

        # Find first "digit" in line
        first_digit_match = next(digit_iter)
        first_digit = digit_dict.get(
            first_digit_match.group(1),
            first_digit_match.group(1),
        )

        # By default, the last "digit" is the first "digit"
        last_digit_match = first_digit_match
        # Find last "digit" in line
        # NOTE: This steps through our iterator, storing the last match
        # to last_digit_match each time. When this loop is done,
        # last_digit_match will contain the last match.
        for last_digit_match in digit_iter:
            pass
        last_digit = digit_dict.get(
            last_digit_match.group(1),
            last_digit_match.group(1),
        )

        # Value = first digit concatenated with last digit, as a number
        calibration_value = int(first_digit + last_digit)
        calibration_sum += calibration_value

    return calibration_sum


parts = (aoc2023_day01_part1, aoc2023_day01_part2)
