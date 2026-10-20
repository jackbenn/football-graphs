# Backlog — football-graphs

Prefix: FBALL · Next ID: 19 · Schema: v1

A visualization of an American football game: one axis shows the position of
the ball, the other time, either clock time or the play number. So far there
is play-by-play data for 2018 and one notebook experimenting with plots of a
single game.

## [FBALL-12] Download the data and build the game files on a schedule

- **Status:** done
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-9, FBALL-11
- **Tags:** data, infra
- **Related:** FBALL-18
- **Commits:** 24afda2

Fetch the nflverse play-by-play for the current season and write one JSON
file per game from `game_data`, plus an index of the season's games for the
page's controls (FBALL-13), where nginx can serve them. The data is
refreshed daily in season, so daily in season and rarely out of it is
enough.

Settled by FBALL-11: the output is the per-game JSON, not raw CSVs. Store
the files gzipped for nginx's `gzip_static`.

Decided 2026-10-19: it runs on GitHub Actions, not the host. The repo is
public, so standard runners are free, and their memory makes the 512 MB
full-season load a non-issue (on the host it would need `usecols`).
- A workflow on a `schedule`, daily in season, builds the current season
  and uploads a tarball of its JSON as an asset on a GitHub release, the
  way nflverse publishes its own data. Schedule it after nflverse's nightly
  refresh. It also takes `workflow_dispatch` with a season, for rebuilds and
  FBALL-18.
- A cron line on the host (`setup-server.sh` already installs one for
  certificate renewal) `curl`s the tarball daily and unpacks it where nginx
  serves it. No Python on the host, no deploy keys in GitHub, no inbound
  port for GitHub to reach.
- Not chosen: committing the JSON to a data branch (history grows every
  day), pushing over SSH from Actions (a key in GitHub secrets and port 22
  open to GitHub's ranges), S3 (AWS credentials for little gain).

GitHub disables scheduled workflows in a public repo after 60 days without
activity, which the off-season exceeds. Decided 2026-10-19: re-enable it by
hand each September, rather than a heartbeat commit.

A change to the JSON format means rebuilding every season's files, so the
build should be one command that FBALL-18 can run for any season.

(nflverse's answer to the 60-day pause is a monthly workflow that commits a
`.heartbeat` file to the default branch.)

### Acceptance criteria
- [x] `python -m football_graphs.build SEASON` downloads the season and
  writes `SEASON/<game_id>.json.gz` for every game and `SEASON/index.json.gz`
  listing them, reading only the columns it uses
- [x] The build fails if any game's final score doesn't match `home_score`
  and `away_score`, so a new quirk stops the publish
- [x] A workflow runs it daily from September to February after nflverse's
  09:03 UTC refresh, and by hand for any season, and uploads `SEASON.tar`
  to a release named `games`
- [x] A test builds 2018 and checks the index against the files

### Notes
- 2026-10-19: first run by hand, for 2018, succeeded in 25 s (7 s building);
  the `games` release's `2018.tar` is byte-identical to a local build. The
  first scheduled run, 2026-10-20 10:00 UTC, is still to check.

## [FBALL-13] Game page on the website

- **Status:** done
- **Priority:** P3
- **Size:** multi
- **Depends on:** FBALL-9, FBALL-11, FBALL-12
- **Tags:** web
- **Commits:** b7f6049, ce76b97

A page at bennetto.com/football where a visitor selects a game through some
controls and sees its graph, drawn in the browser with D3 from the game's
precomputed JSON (FBALL-11). The work is porting `draw_game` to D3, the
controls, and the deployment: adding this repo as a submodule of
`bennetto-infra`, an nginx route for `/football/` serving the page and the
JSON as static files, and a row in `DEPLOY.md`, following `gengo` and
`taking_the_story`. There is no app server, so it may not need a container
of its own, only files nginx can reach. Deployed through the `publish-site`
skill.

Choosing a game, decided 2026-10-19:
- A pageable list of games, most recent first, about 20 to a page, under
  the graph, which is full width at the top.
- Multi-select filters for year, week and team: any of the values chosen
  within a filter, and all filters together. Two teams means either team's
  games, not only the games between them.
- Weeks are 1–18, then WC, DIV, CONF, SB. nflverse numbers playoff weeks on
  from the regular season, whose length has changed (17 weeks until 2020,
  18 since), so the build should add the round to each game in the index.
- A game is always shown: the one in the URL (`?game=<game_id>`), or else
  the most recent. Changing filters changes the list, not the graph; the
  shown game is highlighted in the list.
- With no year filter the list spans every season, so the page fetches
  every season's index on load (a few KB gzipped each). The list of seasons
  can come from nginx (`autoindex_format json` on the games directory) or
  from a `seasons.json` the host's cron line writes.

Also decided: the URL holds only the game, not the filters. Two teams stay
OR, with no head-to-head toggle for now; the only clear alternative is
separate "team 1" and "team 2" filters (without home and away). The phone
layout is parked.

Changed 2026-10-20: the team filter takes one team, not several, and the
year filter names each season by the years it spans (2026–27).

The page must credit nflverse, link to CC BY 4.0, and say the data was
changed (FBALL-17). Use the team names and colors, not the logos.

The host's side of FBALL-12 belongs here too, with the nginx route: a cron
line that fetches `SEASON.tar` from the `games` release daily and unpacks
it where nginx serves `/football/`. The files are gzipped only, so the
route needs `gzip_static on` (and `gunzip on` for any client that doesn't
accept gzip).

### Acceptance criteria
- [x] The build's index labels each game's week 1–18, WC, DIV, CONF or SB
- [x] A page draws a game from its JSON with D3, matching `draw_game`, and
  credits nflverse with a link to CC BY 4.0
- [x] The page has the filters and paged list described above, and always
  shows a game: `?game=<game_id>`, or else the most recent
- [x] bennetto.com/football serves the page and the game files, gzipped,
  with the host fetching each season's tarball daily, and a row in
  `DEPLOY.md`; deployed through `publish-site`

### Notes
- 2026-10-20: deployed. The infra side is bennetto-infra 84e6f1a (route,
  mounts, `fetch-football.sh`, `DEPLOY.md`) and 99704be (a `deploy.sh` fix).
  The repo moved into `bennetto-infra` as a submodule, and its branch from
  `master` to `main`. The first files published were built before 07176a9 and
  lacked the clock fields; rebuilt the same day.

## [FBALL-14] Play details on click or hover

- **Status:** done
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-13
- **Tags:** web
- **Related:** FBALL-17
- **Commits:** 5c59792

Clicking, or perhaps mousing over, a play on the graph shows its details:
at least the description (`desc`), down and distance, and the clock. Those
go into `game_data` as a list of plays, which roughly doubles a game's JSON
(still about 10 KB gzipped), and the D3 page shows them from there.

From FBALL-17: the descriptions are the NFL's own wording, not covered by
nflverse's license. Decided 2026-10-19 to show `desc` anyway. If that ever
has to change, build a description from the plain facts instead (down,
distance, clock, yards, play type).

Since 7442e2c each play in `game_data` has its description, down and
distance, quarter and clock, so this is only the D3 side.

Decided 2026-10-20:
- Hovering over a play highlights its column, across all three panels, and
  shows its details; clicking pins them, and clicking again or Escape
  unpins. Each play's column is the full height of the graph, since many
  plays have no marker.
- The details go in a box above the graph, on the left, beside the legend.
  It shows only `desc`.
- With a play pinned, the left and right arrow keys step to the previous
  and next play.
- A little more space between the three panels.

`desc` starts with the clock on about 90% of plays, but not on kickoffs,
extra points or two-point tries, and never says the quarter. Decided
2026-10-20 to show the plain `desc` anyway, to keep it minimal until it's
been seen; prefixing the quarter and clock from the play's own fields would
cover both.

### Acceptance criteria
- [x] Hovering over any part of a play's column, in any panel, highlights
  the column and shows the play's `desc` in a box above the graph, left of
  the legend
- [x] Clicking pins a play's details until a second click or Escape; while
  pinned, hovering shows nothing else
- [x] With a play pinned, ← and → pin the previous and next play
- [x] More space between the score, game and clock panels

## [FBALL-18] Build the game files for past seasons

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-12
- **Tags:** data
- **Related:** FBALL-10, FBALL-11

Run FBALL-12's build for every past season nflverse has (1999 on), once,
and again whenever the JSON format changes, by running its workflow by hand
(`workflow_dispatch`) for each season, each publishing its own tarball. About 10 s a season on the
laptop. Older seasons may have data quirks `game_data` hasn't met, so run
the season-wide tests (FBALL-10) on every season built, not only 2018, and
fix what they find.
