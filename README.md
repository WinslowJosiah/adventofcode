# adventofcode

My solutions to [Advent of Code](https://adventofcode.com/).

## Usage

To run a solution for a given year and day, run `aoc` with the following
options:

| Short Option | Long Option   | Parameter(s)                                | Explanation                                                                                                                                                                                                                                            |
| ------------ | ------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-h`         | `--help`      | none                                        | Show a help message and exit.                                                                                                                                                                                                                          |
| `-y`         | `--year`      | `n`, an integer                             | The year for which to run the solution.                                                                                                                                                                                                                |
| `-d`         | `--day`       | `n`, an integer between `1` and `25`        | The day for which to run the solution.                                                                                                                                                                                                                 |
| `-b`         | `--benchmark` | `n`, a non-negative integer (default `100`) | The solution will be benchmarked; it will be run `n` times, then the time will be averaged and reported. (If the option is left out, the solution is not benchmarked.)                                                                                 |
| `-i`         | `--input`     | one or more filepaths                       | Each of the files specified by the paths will be passed as input to the solution. If the path is relative, it will be treated as relative to the directory of the solution. (If the option is left out, all files in the solution directory are used.) |

## Examples

These examples assume that the project's root directory is opened in your
favorite terminal.

Run 2023 Day 1:

    py aoc -y 2023 -d 1

Run 2023 Day 7, and benchmark (with 100 runs by default):

    py aoc -y 2023 -d 7 -b

Run 2023 Day 13, and benchmark with 1,000 runs:

    py aoc -y 2023 -d 13 -b 1000

Run 2023 Day 18 on `example.txt`:

    py aoc -y 2023 -d 18 -i example.txt

## init_year.py

`init_year.py` is for automatically initializing the files for a new year. To
use it, simply run it and give it a year value. (This file is intended for my
personal use, but I thought I'd add it to this repo anyway.)
