# Backlog — football-graphs

Prefix: FBALL · Next ID: 17 · Schema: v1

A visualization of an American football game: one axis shows the position of
the ball, the other time, either clock time or the play number. So far there
is play-by-play data for 2018 and one notebook experimenting with plots of a
single game.

## [FBALL-1] Collaborate with Claude inside the notebook

- **Status:** done
- **Priority:** P2
- **Size:** session
- **Depends on:** none
- **Tags:** exploration
- **Related:** FBALL-5
- **Commits:** abcfc31, 335537c

Use this project as an exercise in working with Claude inside a notebook,
before improving the visualization itself.

Open questions to settle when refining it:
- Where the collaboration happens: Jupyter, VS Code, or Claude Code editing
  the `.ipynb` directly.
- How Claude sees results. Outputs exist only after the cells are run, so
  either Jack runs them and Claude reads the saved notebook, or Claude
  executes it itself.
- Whether outputs stay in git at all (FBALL-5).

### Notes
- 2026-10-19: Settled on marimo with the `marimo-pair` skill, after
  comparing it with JupyterLab plus jupyter-mcp-server, VS Code with the
  Claude Code extension, and `# %%` scripts. `EDA.ipynb` was converted to
  `EDA.py` with `marimo convert`. Jack runs `marimo edit --no-token EDA.py`
  from the project's `.venv`; Claude connects to the same kernel through the
  skill's `execute-code.sh`.
- 2026-10-19: What was learned. The kernel really is shared both ways: cells
  Claude creates and runs appear live in Jack's browser, and Claude reads
  Jack's edits and outputs from the kernel without a save. While the
  notebook is open, Claude must change cells through `marimo._code_mode`,
  not by editing `EDA.py`, which the kernel rewrites on save. A cell joins
  the dataflow graph only once it has run, so until the whole notebook has
  run once, running a cell does not re-run the ones below it. Claude cannot
  tell who ran a cell, only the resulting state. A stray edit in the browser
  (`COmm` in the last cell) was committed unnoticed, so read the diff before
  committing `EDA.py`. The skill needs `jq`, and installing it (a
  third-party skill) needed Jack's approval.

## [FBALL-2] Declare the dependencies

- **Status:** idea
- **Priority:** P2
- **Size:** quick
- **Depends on:** none
- **Tags:** config

No `requirements.txt` or equivalent. The notebook imports `numpy`, `pandas`
and `matplotlib`, and was last run on Python 3.6.7. Found by `project-init`
(META-1), 2026-10-19.

## [FBALL-3] Add a `## Getting started` section to the README

- **Status:** idea
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** docs

The README is a title, one line, and a note on where the data came from. It
needs setup, run, and what is not in the repo (the 2014–2017 data, if it stays
in use), for a reader coming to it cold. Run META-6's `repo-docs` skill once
it exists. Found by `project-init` (META-1), 2026-10-19.

## [FBALL-4] Make the notebook run from a fresh clone

- **Status:** done
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** data
- **Commits:** bc22120, abcfc31

Cell 4 of `EDA.ipynb` loads `pbp-2014.csv` through `pbp-2018.csv` from
`data/`, but only `pbp-2018.csv` is in the repo, so the notebook fails on a
fresh clone. The plotting uses a single 2018 game (`GameId` 2018090902). Either
load only 2018, or get the other years and say where they come from. Whether
nflsavant.com still serves them is unchecked. Found by `project-init`
(META-1), 2026-10-19.

### Notes
- 2026-10-19: nflsavant now serves nflverse data in a new 372-column format,
  so the notebook moved to nflverse directly
  (`github.com/nflverse/nflverse-data`, release `pbp`), which is refreshed
  daily in season. A cell in `EDA.py` downloads one season into `data/`, now
  ignored, and the old `pbp-2018.csv` is gone. Checked by running `EDA.py`
  in an empty directory: it downloads and loads the data.

## [FBALL-5] Keep the notebook's outputs out of git, or small

- **Status:** done
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** config
- **Related:** FBALL-1
- **Commits:** abcfc31, bd31547

`EDA.ipynb` is 2.2 MB, of which 5.6 KB is code and markdown; the rest is
output, mostly whole DataFrames displayed with `pd.options.display.max_rows =
None`. One commit (`b242572`) was a 53,000-line diff. Options: stop displaying
whole frames, strip outputs on commit (`nbstripout`), or pair the notebook
with a script (`jupytext`). Matters for FBALL-1, since a collaborator reads
and diffs the notebook. Found by `project-init` (META-1), 2026-10-19.

### Notes
- 2026-10-19: Solved by moving to marimo (FBALL-1). `EDA.py` is plain Python
  with no outputs; marimo keeps outputs in `__marimo__/session/`, now ignored.
  The old `EDA.ipynb`, outputs and all, is still in the repo.

## [FBALL-6] Score graph below the game plot

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** none
- **Tags:** rendering
- **Related:** FBALL-7

Add a second graph below the game plot, sharing its x axis, showing the
score of each team over the game.

`plot_game` already keeps a running score for each team as it draws the
labels, so the data is there; the work is the shared-axis layout (the
function currently takes a single `ax`) and the look of the score lines, in
the team colors.

## [FBALL-7] Bar graph of the clock time each play takes

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** none
- **Tags:** rendering
- **Related:** FBALL-6

Add another graph below the game plot, sharing its x axis, with a bar for
each play showing how much clock time it took. Color the bars, each in a
different color, by what stopped the clock: the next play, an incomplete
pass, a time-out, and so on.

The nflverse data has columns for most of the reasons, including
`incomplete_pass`, `out_of_bounds`, `timeout`, `penalty`, `touchdown`,
`interception`, `fumble_lost` and `quarter_end`, but no two-minute-warning
rows, so that reason would have to come from the clock itself. Working out
which reason applies to each play, and in what order to check them, is most
of the work.

## [FBALL-8] Graphical cleanup of the game plot

- **Status:** idea
- **Priority:** P2
- **Size:** session
- **Depends on:** none
- **Tags:** rendering

A batch of small fixes to `plot_game`:
- The first kickoff's star is clipped at the left edge.
- The quarter lines run through the end zones and cover the score labels;
  stop them at the 0-yard lines.
- The yard lines don't draw at a consistent weight, and could be softer.
- Label the `no_play` line style "penalty" in the legend, unless other kinds
  of no-play show up (timeouts are `no_play` too, but are already skipped).
- Show the yard-line numbers on both sides of the plot.
- No tick marks on the gridlines at the back of the end zones.
- Put a touchdown's score label between the touchdown and the extra point (or
  two-point try), not at the touchdown.

### Acceptance criteria
- [ ] Each fix above is visible on the 2018090902 game and on one game whose
  first play isn't at x=0
- [ ] Every 2018 game still ends on its real final score

## [FBALL-9] Move the data and plotting code out of the notebook

- **Status:** idea
- **Priority:** P2
- **Size:** session
- **Depends on:** FBALL-2
- **Tags:** refactor
- **Related:** FBALL-10, FBALL-11

Move the download, loading, `add_time_column`, `add_yards_column`,
`pick_colors` and `plot_game` into a Python package that `EDA.py` imports, so
the code can be tested (FBALL-10) and run by the website.

Worth splitting `plot_game` while doing it: one function that turns a game's
rows into data (segments with their style, markers, score labels, team colors,
quarter boundaries) and one that draws that data with matplotlib. The scoring
logic is the part most worth testing, and if the web page draws in the
browser (FBALL-11), it can draw from that same data as JSON.

Moving code that the notebook imports changes the pairing workflow: marimo
won't pick up edits to an imported module without a reload, so check how
that feels before moving everything.

## [FBALL-10] Tests

- **Status:** idea
- **Priority:** P2
- **Size:** session
- **Depends on:** FBALL-9
- **Tags:** test

Start with the checks already run by hand while building the plot: every 2018
game's final score matches `home_score` and `away_score`, no two score labels
on the same side are within two plays of each other, and `pick_colors` finds a
distinct pair for every matchup without falling back to grey. Add small
hand-built cases for the scoring edge cases: a defensive touchdown, a
punt-return safety, a defensive two-point return, a game whose first play
isn't a kickoff. The season-wide checks need the downloaded data, so they may
want marking as slow.

## [FBALL-11] Decide how the game page is built and where it runs

- **Status:** question
- **Priority:** P2
- **Size:** session
- **Depends on:** none
- **Tags:** web
- **Related:** FBALL-9, FBALL-12, FBALL-13

The aim is a page at bennetto.com/football where a visitor picks a game and
sees its graph, with details of a play on click or hover. This repo becomes a
submodule of `bennetto-infra`, like `gengo` and `taking_the_story`, rather
than part of `website`. The site is one Docker Compose stack on an EC2 host
(`bennetto-infra/DEPLOY.md`), with each app its own container behind nginx.

Questions to settle:
- Where the drawing happens. Matplotlib images from a server are closest to
  the notebook but make hover details awkward; drawing in the browser (D3,
  Plotly, Vega-Lite) from JSON makes them easy but means a second renderer.
- Whether the container needs an app server at all. A season is a few
  hundred games, so the per-game JSON could be precomputed by the scheduled
  download (FBALL-12) and served as static files from the container, which
  also makes caching (FBALL-16) moot.
- How a visitor picks a game: season, week, team.

The output is revised items FBALL-12 to FBALL-16, not code.

## [FBALL-12] Download the data on a schedule

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-9, FBALL-11
- **Tags:** data, infra

Fetch the nflverse play-by-play regularly, where the site can read it. It is
refreshed daily in season, so daily in season and rarely out of it is
enough. Where it runs (cron on the host, a container, a GitHub Action) and
what it produces (raw CSVs, or per-game files ready to serve) depend on
FBALL-11.

## [FBALL-13] Game page on the website

- **Status:** idea
- **Priority:** P3
- **Size:** multi
- **Depends on:** FBALL-9, FBALL-11, FBALL-12
- **Tags:** web

A page at bennetto.com/football where a visitor selects a game through some
controls and sees its graph. Includes adding this repo as a submodule of
`bennetto-infra`, with its own Compose service and Dockerfile, an nginx route
for `/football/`, and a row in `DEPLOY.md`, following `gengo` and
`taking_the_story`. Deployed through the `publish-site` skill.

## [FBALL-14] Play details on click or hover

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-13
- **Tags:** web

Clicking, or perhaps mousing over, a play on the graph shows its details:
at least the description (`desc`), down and distance, and the clock.

## [FBALL-15] Display options on the game page

- **Status:** idea
- **Priority:** P4
- **Size:** unknown
- **Depends on:** FBALL-13
- **Tags:** web
- **Related:** FBALL-6, FBALL-7

Options for how the graph is shown. The play number or clock time on the x
axis is the one that exists now; the score and clock-time panels (FBALL-6,
FBALL-7) could be others.

## [FBALL-16] Cache rendered games

- **Status:** idea
- **Priority:** P5
- **Size:** unknown
- **Depends on:** FBALL-13
- **Tags:** web, performance

Cache games if rendering them on demand starts getting expensive. Very long
term, and may be unnecessary if FBALL-11 settles on precomputed files.
