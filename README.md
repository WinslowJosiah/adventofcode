# adventofcode

My solutions to [Advent of Code](https://adventofcode.com/).

## Usage

To run a solution for a given year and day, run `__main__.py` with the following options:

| Short Option | Long Option | Parameter(s) | Explanation |
|---|---|---|---|
| `-h` | `--help` | none | Show a help message and exit. |
| `-y` | `--year` | `n`, an integer | The year for which to run the solution. |
| `-d` | `--day` | `n`, an integer between `1` and `25` | The day for which to run the solution. |
| `-b` | `--benchmark` | `n`, a non-negative integer (default `100`) | The solution will be benchmarked; it will be run `n` times, then the time will be averaged and reported. (If the option is left out, the solution is not benchmarked.) |
| `-i` | `--input` | one or more filepaths | Each of the files specified by the paths will be passed as input to the solution. If the path is relative, it will be treated as relative to the directory of the solution. (If the option is left out, all files in the solution directory are used.) |
