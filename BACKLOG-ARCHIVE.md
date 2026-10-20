# Backlog archive — football-graphs

Prefix: FBALL · Archive of: BACKLOG.md · Schema: v1

Completed and dropped items, kept for the rationale rather than the status.
IDs are assigned from the same sequence as `BACKLOG.md`, which holds the
authoritative `Next ID`.

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

- **Status:** done
- **Priority:** P2
- **Size:** quick
- **Depends on:** none
- **Tags:** config
- **Commits:** e2f020f

No `requirements.txt` or equivalent. The notebook imports `numpy`, `pandas`
and `matplotlib`, and was last run on Python 3.6.7. Found by `project-init`
(META-1), 2026-10-19.

Done as part of FBALL-9: lower bounds only for now, exact pins left until the
Docker image (FBALL-13) needs them.

### Acceptance criteria
- [x] `pyproject.toml` declares the runtime dependencies with lower bounds,
  and marimo in a `dev` extra
- [x] The README's install steps use it

## [FBALL-3] Add a `## Getting started` section to the README

- **Status:** done
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** docs

The README is a title, one line, and a note on where the data came from. It
needs setup, run, and what is not in the repo (the 2014–2017 data, if it stays
in use), for a reader coming to it cold. Run META-6's `repo-docs` skill once
it exists. Found by `project-init` (META-1), 2026-10-19.

### Notes
- 2026-10-19: Written by hand rather than with META-6's `repo-docs` skill,
  which doesn't exist yet. The 2014–2017 data is no longer used. Added a
  `CLAUDE.md` alongside it with the notebook-pairing rules.

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

## [FBALL-6] Score graph above the game plot

- **Status:** done
- **Priority:** P3
- **Size:** session
- **Depends on:** none
- **Tags:** rendering
- **Related:** FBALL-7
- **Commits:** 1c6266b

Add a second graph below the game plot, sharing its x axis, showing the
score of each team over the game.

`plot_game` already keeps a running score for each team as it draws the
labels, so the data is there; the work is the shared-axis layout (the
function currently takes a single `ax`) and the look of the score lines, in
the team colors.

Since 7442e2c each play in `game_data` carries both teams' scores after
it, so the score lines need no more data; drawing them belongs in the D3
page (FBALL-13), which shares the play-number x axis.

Changed 2026-10-19: the score graph goes above the game graph, not below,
with no x-axis labels (the quarters are labeled under the clock bars), and
an extra point shows as its own step, not merged with its touchdown.
Otherwise it is a step line per team, in the team colors.

### Acceptance criteria
- [x] Above the game graph, on its x axis, a step line of each team's score
  in its color, with the quarters marked but not labeled
- [x] A touchdown and its extra point are separate steps

## [FBALL-7] Bar graph of the clock time each play takes

- **Status:** done
- **Priority:** P3
- **Size:** session
- **Depends on:** none
- **Tags:** rendering
- **Related:** FBALL-6
- **Commits:** 07176a9, e2b54c8

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

Since 7442e2c each play in `game_data` has its game clock (`time`, with
regular-season overtime at 10 minutes), its quarter and clock, and the
timeouts called after it, so the bars' lengths are there. Still to add, in
`game_data`, where it can be tested: the reason the clock stopped, from the
columns above, and the last play of each quarter running to the quarter's
end rather than to the next snap.

Started 2026-10-19. Each play in `game_data` now has `duration`, the
seconds of game clock to the next snap (to the end of the period for the
last play of one), and `stop`, the first that applies of: `quarter_end`,
`two_minute_warning`, `timeout`, `score` (tries included), `turnover`
(interception, lost fumble, turnover on downs), `kick`, `incomplete`
(spikes included), `penalty`, `out_of_bounds`, else `running`. What the
2018 season showed:
- Out of bounds stops the clock for good only in the last 2:00 of the first
  half and the last 5:00 of the second half and of overtime (overtime
  follows the five-minute rule in the data). Earlier it restarts at the
  ready signal, taking about 34 s against 39 s for a running play, so it
  counts as `running`.
- A penalty counts at any time: an incomplete pass wiped out by a penalty
  has `incomplete_pass` 0, so `penalty` is the only sign the clock stopped.
- 46 plays in 2018 are out of order by `play_id`, so the clock runs
  backwards; their `duration` is None. Sorting by clock instead would
  move them in the main plot too, so it is left alone.
- The page groups the ten reasons into eight colors: kicks and turnovers
  as "change of possession", the two-minute warning with the end of the
  quarter. Bars are clipped at 1:00; each has a tooltip.

### Acceptance criteria
- [x] Each play in `game_data` has its clock `duration` and a `stop` reason,
  tested on hand-built games and checked across the 2018 season
- [x] The page draws a bar per play below the game graph, sharing its x
  axis, colored by `stop`, with a legend
- [x] The notebook's matplotlib plot gets the same panel, or it is decided
  that it stays D3-only

### Notes
- 2026-10-19: decided D3-only; the matplotlib plot is deprecated (a258949).
  The legend became a list beside the game list, in groups of like reasons
  with like colors, and "clock running" became "clock kept running".

## [FBALL-8] Graphical cleanup of the game plot

- **Status:** done
- **Priority:** P2
- **Size:** session
- **Depends on:** none
- **Tags:** rendering
- **Commits:** 43611e2

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
- A kickoff called back by a penalty is a `no_play` with the receiving team
  as `posteam`, so it is drawn as an ordinary play in the receiving team's
  color, not a star in the kicking team's. There are 13 in 2018, including
  the opening kickoff of 2018102500; `kickoff_attempt` marks them.

### Acceptance criteria
- [x] Each fix above is visible on the 2018090902 game and on one game whose
  first play isn't at x=0
- [x] Every 2018 game still ends on its real final score

### Notes
- 2026-10-19: done on the D3 page instead, since `plot_game` is now
  deprecated; the two data fixes (the touchdown label's place, the
  called-back kickoff) are in `game_data`, so the deprecated plot gets them
  too. Checked on 2018090902 (2018_01_CIN_IND) and 2018102500
  (2018_08_MIA_HOU). Every `no_play` in 2018 is a penalty (57 are
  offsetting, with `penalty` NaN), so the legend says just "penalty".

## [FBALL-9] Move the data and plotting code out of the notebook

- **Status:** done
- **Priority:** P2
- **Size:** session
- **Depends on:** FBALL-2
- **Tags:** refactor
- **Related:** FBALL-10, FBALL-11
- **Commits:** e2f020f, 36a4c68

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

Decided 2026-10-19: a `src/football_graphs/` package (`data`, `colors`,
`game`, `plot`) installed editable; marimo's `auto_reload = "autorun"`; the data
directory a parameter defaulting to `data`; the exploration cells stay in
`EDA.py`; the split of `plot_game` done in this item, as a separate commit
after the plain move.

### Acceptance criteria
- [x] `EDA.py` imports the download, loading, column, color and plotting code
  from the package, and the download cell still defines only `_` names
- [x] Both plots of 2018090902 are pixel-identical before and after the move,
  and after the split
- [x] `plot_game` is split into a function that returns the game's data and
  one that draws it
- [x] Every 2018 game still ends on its real final score

## [FBALL-10] Tests

- **Status:** done
- **Priority:** P2
- **Size:** session
- **Depends on:** FBALL-9
- **Tags:** test
- **Commits:** 5f82c71

Start with the checks already run by hand while building the plot: every 2018
game's final score matches `home_score` and `away_score`, no two score labels
on the same side are within two plays of each other, and `pick_colors` finds a
distinct pair for every matchup without falling back to grey. Add small
hand-built cases for the scoring edge cases: a defensive touchdown, a
punt-return safety, a defensive two-point return, a game whose first play
isn't a kickoff. The season-wide checks need the downloaded data, so they may
want marking as slow.

Found while starting it, 2026-10-19: the closest same-side labels in 2018
are two plays apart (a field goal, the kickoff, then a defensive touchdown),
so the label check fails below two. The one game whose first play isn't a
`kickoff` (2018102500) opens with a kickoff wiped out by a penalty, a
`no_play` whose `posteam` is the receiving team.

### Acceptance criteria
- [x] `pytest` runs the tests, and pytest is in the `dev` extra
- [x] Season-wide: every 2018 game ends on `home_score` and `away_score`,
  and no two labels on the same side are under two plays apart; marked slow
  and skipped without the downloaded data
- [x] `pick_colors` finds a pair without grey for every ordered pair of teams
  in the teams table
- [x] Hand-built games, needing no downloaded data, for a defensive
  touchdown, a punt-return safety, a defensive two-point return and a game
  whose first play isn't a kickoff

## [FBALL-11] Decide how the game page is built and where it runs

- **Status:** done
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

### Decision
2026-10-19, for a t3.micro with little else on it, and a page that should
show a game within a few seconds:
- **Drawing in the browser, with D3**, from the JSON of `game_data`. Measured
  on the laptop (M1): a game's JSON is 32 KB, 4.4 KB gzipped, and drawing it
  in the browser is well under 100 ms whatever the server's CPU credits.
  Matplotlib on the server took 430 ms per game for one panel on the laptop,
  likely 2–3 s with the FBALL-6/7 panels on a t3.micro with credits and far
  more without, and makes hover awkward. D3 over Vega-Lite or Plotly because
  `draw_game` is imperative, mark by mark, so it ports nearly line for line,
  and the bundle is about 90 KB gzipped against Plotly's 1 MB. The cost is a
  second renderer beside the notebook's matplotlib one.
- **Everything precomputed, past seasons included**, as static files served
  by nginx, with no app server. Computing past seasons on demand would need
  an always-on pandas process on a 1 GB host and the raw CSVs on disk (18 MB
  a season, more than the finished JSON), and a season's first request
  would take several seconds. Precomputing a season takes about 10 s on the
  laptop; every season since 1999 is a few minutes, and about 100 MB stored
  gzipped. Caching (FBALL-16) is dropped.
- Loading a full season peaks at 512 MB; only the ~25 columns used, 33 MB.
  Anything that loads a season on the host must use only those columns.

Still open, for FBALL-13: how a visitor picks a game (season, week, team).

## [FBALL-15] Display options on the game page

- **Status:** dropped
- **Reason:** No display by clock time is wanted, and there are no other options in sight; the FBALL-6/7 panels are just part of the graph.
- **Priority:** P4
- **Size:** unknown
- **Depends on:** FBALL-13
- **Tags:** web
- **Related:** FBALL-6, FBALL-7

Options for how the graph is shown. The play number or clock time on the x
axis is the one that exists now; the score and clock-time panels (FBALL-6,
FBALL-7) could be others.

Every point in `game_data` has both x values, so switching the x axis needs
no new files and can happen entirely in the browser.

## [FBALL-16] Cache rendered games

- **Status:** dropped
- **Reason:** FBALL-11 settled on precomputed static files: nothing is rendered on demand, so there is nothing to cache.
- **Priority:** P5
- **Size:** unknown
- **Depends on:** FBALL-13
- **Tags:** web, performance

Cache games if rendering them on demand starts getting expensive. Very long
term, and may be unnecessary if FBALL-11 settles on precomputed files.

## [FBALL-17] Check the nflverse data license

- **Status:** done
- **Priority:** P2
- **Size:** quick
- **Depends on:** none
- **Tags:** data
- **Related:** FBALL-11, FBALL-13

Find the license of the nflverse play-by-play and teams data, and whatever
the NFL's own terms say about the play-by-play underneath it. Only reading
it in a notebook needs nothing, but serving it on bennetto.com/football
(FBALL-13), and showing play descriptions (FBALL-14), may need attribution or
may not be allowed. Record the answer in the README's Data section, and in
new items if it changes the plan.

### Answer
2026-10-19, recorded in the README's Data section: nflverse's `pbp` and
`teams` data are CC BY 4.0 (the `LICENSE.md` of nflverse-data and of
nflverse-pbp; nflreadpy says the same of all nflverse data except FTN's
charting data, which is CC BY-SA and not used here). Serving it, or files
built from it, needs a credit to nflverse, a link to the license and a note
that it was changed. The play-by-play underneath comes from the NFL's feeds,
which nflverse can't license: game facts aren't copyrightable in the US, but
the play descriptions are the NFL's wording. Not a lawyer's answer; it
doesn't change the plan, but FBALL-13 gets the credit and FBALL-14 the open
question about `desc`.
