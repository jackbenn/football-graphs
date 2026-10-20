# Football Graphs

Graphing American football games. Each game is drawn as the ball's position
on the field (one end zone at the bottom, the other at the top) against the
play number or the game clock: a line for each play, styled by the kind of
play, in the two teams' colors, with the score marked at each score.

So far it is one [marimo](https://marimo.io) notebook, `EDA.py`, exploring
the 2018 season and plotting one game. The plan, including a page at
bennetto.com/football, is in [`BACKLOG.md`](BACKLOG.md).

## Getting started

You need Python 3.12 or later.

```bash
python3 -m venv .venv
.venv/bin/pip install marimo numpy pandas matplotlib
.venv/bin/marimo edit EDA.py
```

The dependencies are not pinned yet (FBALL-2). The notebook was last run with
marimo 0.25.1, numpy 2.5.4, pandas 3.0.6 and matplotlib 3.11.2.

The data is not in the repo. On a fresh clone, run the download cell near the
top of the notebook by hand (it does not run automatically). It saves a
season's play-by-play and the table of teams into `data/`, which is ignored
by git. Change `_year` in that cell for another season, and the year and
`old_game_id` in the cells below it for another game. Delete a file in
`data/` to fetch a fresh copy.

`EDA.py` is plain Python, so it also runs as a script once the data is
downloaded: `.venv/bin/python EDA.py`.

## Data

Play-by-play and team colors come from
[nflverse](https://github.com/nflverse/nflverse-data) (the `pbp` and `teams`
releases), which is refreshed daily during the season. The data is not
covered by this repository's license, and its own license has not been
checked yet (FBALL-17).

The repo originally used CSVs from [nflsavant.com](http://nflsavant.com/),
which now serves nflverse data in the same format.

## License

The code is under the Apache License 2.0; see [`LICENSE`](LICENSE).
