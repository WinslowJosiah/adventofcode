# adventofcode

My solutions to [Advent of Code](https://adventofcode.com).

The solution template I use is a modified version of David Brownman's amazing
[Python solution template](https://github.com/xavdid/advent-of-code-python-template).
Python 3.12 or higher is required to run these solutions; if you want to run
them yourself and are having trouble, let me know in [a GitHub issue](https://github.com/WinslowJosiah/adventofcode/issues)
on this repo.

In 2024, I wrote [blog posts](https://winslowjosiah.com/blog/category/advent-of-code)
on my personal website explaining my solutions for each day. Starting in 2025,
I've been rewriting my solutions to use their current template, and writing
step-by-step explanations of them for use on a separate portion of my website:
<https://aoc.winslowjosiah.com>. Check it out if you're interested!

## Usage

To run a solution for a given year and day, run `aoc.py` with the following
options:

| Short Option | Long Option   | Parameter(s)                                | Explanation                                                                            |
| ------------ | ------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- |
| `-h`         | `--help`      | none                                        | Show a help message and exit.                                                          |
| `-y`         | `--year`      | `n`, an integer                             | The year for which to run the solution.                                                |
| `-d`         | `--day`       | `n`, an integer between `1` and `25`        | The day for which to run the solution.                                                 |
| `-t`         | `--test`      | none                                        | If provided, use the test input instead of the full puzzle input.                      |
| N/A          | `--debug`     | none                                        | If provided, print things passed to `self.debug()` within the solution.                |
| `-b`         | `--benchmark` | `n`, a non-negative integer (default `100`) | If provided, benchmark the solution by running it `n` times and averaging the runtime. |
| `-s`         | `--slow`      | none                                        | If provided, run solution functions marked as `@slow` (which aren't run by default).   |
| `-p`         | `--profile`   | none                                        | If provided, profile the solution with `cProfile`.                                     |

### Examples

These examples assume that the project's root directory is opened in your
favorite terminal.

Run 2023 Day 1:

    py aoc.py -y 2023 -d 1

Run 2023 Day 7, and benchmark (with 100 runs by default):

    py aoc.py -y 2023 -d 7 -b

Run 2023 Day 13, and benchmark with 1,000 runs:

    py aoc.py -y 2023 -d 13 -b 1000

Run 2023 Day 18 on the test input:

    py aoc.py -y 2023 -d 18 -t

### start.py

`start.py` is for automatically initializing the files for a new day. It takes
the following options:

| Short Option | Long Option | Parameter(s)                         | Explanation                                     |
| ------------ | ----------- | ------------------------------------ | ----------------------------------------------- |
| `-h`         | `--help`    | none                                 | Show a help message and exit.                   |
| `-y`         | `--year`    | `n`, an integer                      | The year for which to create the solution file. |
| `-d`         | `--day`     | `n`, an integer between `1` and `25` | The day for which to create the solution file.  |

## Solution Blog

I have a blog with full step-by-step explanations of my Advent of Code solutions
at <https://aoc.winslowjosiah.com>. I hope to make it a good resource for anyone
who's stuck on an Advent of Code puzzle, or for anyone who's curious about my
thought process and solutions specifically.

The files for that blog live in the `blog` folder of this repository, and it
updates automatically when I push to it thanks to the magic of [GitHub Pages](https://docs.github.com/en/pages).
I use the [Astro](https://astro.build) framework (mainly because they support
sweet-looking code blocks using [Expressive Code](https://expressive-code.com)),
and it's styled using the [holiday.css](https://holidaycss.js.org) stylesheet.

If you have any feedback about the blog, opening [a GitHub issue](https://github.com/WinslowJosiah/adventofcode/issues)
on this repo is a good place to do that; otherwise, you can contact me through
[Mastodon](https://hachyderm.io/@winslowjosiah), [Twitter](https://twitter.com/WinslowJosiah),
or [my email](mailto:winslowjosiah@gmail.com).

## TODO

- [ ] Complete past AoCs
    - [ ] 2015
    - [ ] 2016
    - [ ] 2017
    - [ ] 2018
    - [ ] 2019
    - [ ] 2020
    - [ ] 2021
    - [ ] 2022
    - [x] 2023
    - [ ] 2024 _(have solved; have not explained on new blog)_
    - [x] 2025
- [ ] Automatically retrieve my puzzle input
- [ ] Automatically submit my answers to the Advent of Code website
