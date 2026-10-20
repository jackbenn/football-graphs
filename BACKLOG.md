# Backlog — football-graphs

Prefix: FBALL · Next ID: 18 · Schema: v1

A visualization of an American football game: one axis shows the position of
the ball, the other time, either clock time or the play number. So far there
is play-by-play data for 2018 and one notebook experimenting with plots of a
single game.

## [FBALL-2] Declare the dependencies

- **Status:** idea
- **Priority:** P2
- **Size:** quick
- **Depends on:** none
- **Tags:** config

No `requirements.txt` or equivalent. The notebook imports `numpy`, `pandas`
and `matplotlib`, and was last run on Python 3.6.7. Found by `project-init`
(META-1), 2026-10-19.

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

## [FBALL-17] Check the nflverse data license

- **Status:** question
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
