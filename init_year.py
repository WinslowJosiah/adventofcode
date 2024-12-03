import pathlib

from jinja2 import Environment, FileSystemLoader


FILE_PATH = pathlib.Path(__file__).parent


def main(year: int):
    environment = Environment(loader=FileSystemLoader(FILE_PATH))
    template = environment.get_template("__init__.py.jinja")

    # Create directory for year
    year_dir = FILE_PATH / f"aoc/{year}"
    year_dir.mkdir(parents=True)

    # For each day from 1 to 25
    for day in range(1, 26):
        # Create directory for day
        day_dir = year_dir / f"day{day:0>2}"
        day_dir.mkdir()

        # Create __init__.py file for day
        aoc_init_path = day_dir / "__init__.py"
        aoc_init_py = template.render(year=year, day=day)
        with open(aoc_init_path, "w", encoding="utf-8") as f:
            f.write(aoc_init_py)


if __name__ == "__main__":
    year = int(input("Enter year: "))
    main(year)
    print(f"Advent of Code {year} files initialized.")
