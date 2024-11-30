from collections.abc import Iterable


def aoc2023_day06_part1(lines: Iterable[str]) -> int:
    def get_distance(button_time: int, race_time: int) -> int:
        """
        Calculate the distance travelled, given the time spent holding
        the button and allotted race time.
        """
        return button_time * (race_time - button_time)

    line_iter = iter(lines)
    # Extract the times and distances from the input lines
    race_times = map(int, next(line_iter).split(":")[1].split())
    race_distances = map(int, next(line_iter).split(":")[1].split())

    # NOTE: The number of ways to win all races is the product of the
    # number of ways to win each race.
    total_wins = 1
    # For each race time and record distance
    for race_time, race_distance in zip(race_times, race_distances):
        # NOTE: To count the ways to win this race, we will search each
        # possible button-hold time from the midpoint down to 1 ms. We
        # only need to search half of them because the distances are
        # symmetric; i.e. there are two ways to get each distance,
        # except the one corresponding to the exact midpoint.
        # OPTIMIZE: This algorithm runs slowly if the number of wins is
        # super large, but for Part 1 this isn't a big concern.

        half_time = race_time // 2
        # If holding the button for half the time (the best strategy)
        # doesn't beat the record
        if get_distance(half_time, race_time) <= race_distance:
            # Nothing will beat the record
            return 0

        wins = 0
        # If the midpoint is exact
        if race_time - half_time == half_time:
            # This counts as 1 win
            wins += 1
            # Prevent the exact midpoint from being checked
            half_time -= 1

        # Search each possible button time from the midpoint to 1
        # NOTE: We omit 0 because it causes the distance to be 0, which
        # can never beat a record.
        for button_time in range(half_time, 0, -1):
            # If this distance doesn't beat the record
            if get_distance(button_time, race_time) <= race_distance:
                # No lower button times will beat the record
                break
            # This corresponds to 2 wins
            wins += 2

        total_wins *= wins

    return total_wins


def aoc2023_day06_part2(lines: Iterable[str]) -> int:
    def get_distance(button_time: int, race_time: int) -> int:
        """
        Calculate the distance travelled, given the time spent holding
        the button and allotted race time.
        """
        return button_time * (race_time - button_time)

    line_iter = iter(lines)
    # Extract the time and distance from the input lines
    race_time = int(next(line_iter).split(":")[1].replace(" ", ""))
    race_distance = int(next(line_iter).split(":")[1].replace(" ", ""))

    # NOTE: The method I actually used to finish Part 2 was the same as
    # my method for Part 1, but with a single race instead. While it did
    # work, and let me finish Part 2 in 19 minutes (!), it took an
    # entire second to run, which is unusually slow. I knew there had to
    # be a better way. So afterwards, I did it again in that better way.

    # At maximum, every button time not at the endpoints will win
    max_wins = race_time - 1

    # If the record is 0
    if race_distance <= 0:
        # Any nonzero distance will beat it
        return max_wins

    half_time = race_time // 2
    # If holding the button for half the time (the best strategy)
    # doesn't beat the record
    if get_distance(half_time, race_time) <= race_distance:
        # Nothing will beat the record
        return 0

    # We will calculate the number of button times (in the first half)
    # that won't win, and subtract it twice from max_wins to get the
    # number of button times in total that win
    # NOTE: We do this with a variant of binary search.
    range_start, range_end = 0, half_time
    # While we haven't converged on the result
    while range_start <= range_end:
        # Calculate midpoint of range, and its race distance
        range_midpoint = (range_start + range_end) // 2
        range_midpoint_distance = get_distance(range_midpoint, race_time)

        # If the distance matches, but doesn't beat, the record
        if range_midpoint_distance == race_distance:
            # The cutoff point is exactly here
            return max_wins - 2 * range_midpoint
        # If the distance beats the record
        elif range_midpoint_distance > race_distance:
            # The cutoff point is before the current midpoint
            range_end = range_midpoint - 1
        # If the distance doesn't match or beat the record
        else:
            # The cutoff point is after the current midpoint
            range_start = range_midpoint + 1

    # The end of the range is the cutoff point (because it's the largest
    # time that doesn't beat the record)
    return max_wins - 2 * range_end


parts = (aoc2023_day06_part1, aoc2023_day06_part2)
