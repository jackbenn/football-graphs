# Football Graphs

Graphing American football games. Each game is drawn as the ball's position
on the field (one end zone at the bottom, the other at the top) against the
play number or the game clock: a line for each play, styled by the kind of
play, in the two teams' colors, with the score marked at each score.

The code is a Python package, `football_graphs` in `src/`: `data` downloads
and loads the play-by-play, `colors` picks the teams' colors, `game` turns a
game's plays into plain data (line segments, markers, score labels, quarter
starts) that can be saved as JSON, and `plot` draws that with matplotlib. A [marimo](https://marimo.io) notebook, `EDA.py`, uses it to
explore the 2018 season and plot one game. The plan, including a page at
bennetto.com/football, is in [`BACKLOG.md`](BACKLOG.md).

## Getting started

You need Python 3.12 or later.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/marimo edit EDA.py
```

The dependencies are in `pyproject.toml`, with lower bounds only; the `dev`
extra adds marimo. The package is installed editable, and the notebook
re-runs the cells that use it when one of its modules is saved
(`auto_reload` in `pyproject.toml`), which takes effect when marimo starts.
It was last run with marimo 0.25.1, numpy 2.5.4, pandas 3.0.6 and
matplotlib 3.11.2.

The data is not in the repo. On a fresh clone, run the download cell near the
top of the notebook by hand (it does not run automatically). It saves a
season's play-by-play and the table of teams into `data/`, which is ignored
by git. Change `_year` in that cell for another season, and the year and
`old_game_id` in the cells below it for another game. Delete a file in
`data/` to fetch a fresh copy.

`EDA.py` is plain Python, so it also runs as a script once the data is
downloaded: `.venv/bin/python EDA.py`.

## Tests

```bash
.venv/bin/pytest                  # everything, about 15 seconds
.venv/bin/pytest -m "not slow"    # skip the checks of the whole 2018 season
```

The tests in `tests/test_game.py` build small games by hand for the scoring
edge cases and need no data. The rest use the downloaded 2018 season and
teams table, and are skipped without them.

## Building the game files

```bash
.venv/bin/python -m football_graphs.build 2018    # or no season, for the current one
```

writes `games/2018/`: a gzipped JSON file for each game, named by its
nflverse `game_id`, and `index.json.gz` listing the games and teams. It
downloads the season first if it isn't in `data/` (`--refresh` to fetch it
again), and exits with an error if any game's final score comes out wrong.

On GitHub, the `build games` workflow runs this every day from September to
February, after nflverse's own refresh, and uploads the season as
`SEASON.tar` to the release named `games`. Run it by hand from the Actions
tab for any other season. GitHub pauses scheduled workflows after 60 days
without activity in the repository, so it may need re-enabling each
September.

## The game page

`web/` is the page for bennetto.com/football: static files with no build
step, drawing a game in the browser with [D3](https://d3js.org) (vendored in
`web/vendor/`, under its own ISC license) from the files the build writes.
To try it locally, build a season or two, then

```bash
.venv/bin/python scripts/serve.py    # http://127.0.0.1:8000/football/
```

which serves the page and `games/` the way nginx does on the site.

## Data

Play-by-play and team colors come from
[nflverse](https://github.com/nflverse/nflverse-data) (the `pbp` and `teams`
releases), which is refreshed daily during the season. The data is not
covered by this repository's license.

nflverse releases it under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
(the `LICENSE.md` of nflverse-data and of nflverse-pbp, which builds the
play-by-play). Anything that shows it, or files built from it, must credit
nflverse, link to the license, and say the data was changed. Checked
2026-10-19.

That license covers what nflverse adds. The play-by-play underneath is
scraped from the NFL's own feeds, and nflreadr says that NFL data "belong to
their respective owners, and are governed by their terms of use". Facts
about a game, such as the ball's position, the down and the score, are not
copyrightable in the US; the play descriptions (`desc`) are the NFL's own
wording, which is less clear. The teams release also has logo URLs, and the
logos are trademarks, so this project uses only the names and colors.

The repo originally used CSVs from [nflsavant.com](http://nflsavant.com/),
which now serves nflverse data in the same format.

## License

The code is under the Apache License 2.0; see [`LICENSE`](LICENSE).
