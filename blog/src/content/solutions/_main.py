from pathlib import *  # pyright: ignore[reportWildcardImportFromLibrary]

YEAR = int(input("Enter year: "))

for day in range(1, 13 if YEAR >= 2025 else 26):
    TEMPLATE = rf"""---
year: {YEAR}
day: {day}
title: "Title"
slug: {YEAR}/day/{day}
# pub_date: "{YEAR + 1}-01-01"
# concepts: []
---
## Part 1

```py title="{YEAR}\day{day:02}\solution.py"
...
```

## Part 2

```py title="{YEAR}\day{day:02}\solution.py"
...
```
"""
    path = (
        Path(__file__).parent / str(YEAR) / f"{day:02}"
    )
    path.mkdir(parents=True)
    (path / "README.md").write_text(TEMPLATE)
