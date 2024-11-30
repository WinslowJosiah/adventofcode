from collections.abc import Iterable


def aoc2023_day02_part1(lines: Iterable[str]) -> int:
    import re

    # The number of cubes to compare each game against
    sample_counts = {"red": 12, "green": 13, "blue": 14}
    # This regex will match games, and group the ID and list of draws
    game_regex = re.compile(r"Game (\d+): (.*)")

    def verify_draws(
            draws_str: str,
            counts: dict[str, int] = sample_counts,
    ) -> bool:
        """
        Verify whether a game, given by the string `draws_str`, is
        possible given certain cube counts.
        """
        # Parsing is fun /s
        for draw_str in draws_str.split("; "):
            for cube_count_str in draw_str.split(", "):
                count, color = cube_count_str.split()
                count = int(count)

                # If count of this color is larger than assumed
                if count > counts.get(color, 0):
                    # This draw is impossible
                    return False

        return True

    possible_games_sum = 0
    for line in lines:
        # Get ID and list of draws for this game
        re_match = game_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        game_id_str, draws_str = re_match.groups()
        # If draws are valid, add ID to sum
        if verify_draws(draws_str):
            possible_games_sum += int(game_id_str)

    return possible_games_sum


def aoc2023_day02_part2(lines: Iterable[str]) -> int:
    from math import prod
    import re

    # This regex will match games, and group the ID and list of draws
    game_regex = re.compile(r"Game (\d+): (.*)")

    def get_min_counts(draws_str: str) -> dict[str, int]:
        """
        Get the minimum number of cubes required for a game, given by
        the string `draws_str`, to be possible.
        """
        counts: dict[str, int] = {}

        # Parsing is fun /s
        for draw_str in draws_str.split("; "):
            for cube_count_str in draw_str.split(", "):
                count, color = cube_count_str.split()
                count = int(count)

                if color not in counts:
                    # Add this count if not present
                    counts[color] = count
                else:
                    # There must be at least this many of this color
                    counts[color] = max(counts[color], count)

        return counts

    power_sum = 0
    for line in lines:
        # Get list of draws for this game
        re_match = game_regex.fullmatch(line)
        assert re_match is not None  # This makes the type checker happy
        _, draws_str = re_match.groups()
        # Get minimum cube counts for this game
        min_counts = get_min_counts(draws_str)
        # Add "power" of counts to sum
        power_sum += prod(min_counts.values())

    return power_sum


parts = (aoc2023_day02_part1, aoc2023_day02_part2)
