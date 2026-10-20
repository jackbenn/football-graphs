# Backlog — football-graphs

Prefix: FBALL · Next ID: 19 · Schema: v1

A visualization of an American football game: one axis shows the position of
the ball, the other time, either clock time or the play number. So far there
is play-by-play data for 2018 and one notebook experimenting with plots of a
single game.

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

Since 7442e2c each play in `game_data` carries both teams' scores after
it, so the score lines need no more data; drawing them belongs in the D3
page (FBALL-13), which shares the play-number x axis.

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

Since 7442e2c each play in `game_data` has its game clock (`time`, with
regular-season overtime at 10 minutes), its quarter and clock, and the
timeouts called after it, so the bars' lengths are there. Still to add, in
`game_data`, where it can be tested: the reason the clock stopped, from the
columns above, and the last play of each quarter running to the quarter's
end rather than to the next snap.

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
- A kickoff called back by a penalty is a `no_play` with the receiving team
  as `posteam`, so it is drawn as an ordinary play in the receiving team's
  color, not a star in the kicking team's. There are 13 in 2018, including
  the opening kickoff of 2018102500; `kickoff_attempt` marks them.

### Acceptance criteria
- [ ] Each fix above is visible on the 2018090902 game and on one game whose
  first play isn't at x=0
- [ ] Every 2018 game still ends on its real final score

## [FBALL-12] Download the data and build the game files on a schedule

- **Status:** active
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
- [ ] A workflow runs it daily from September to February after nflverse's
  09:03 UTC refresh, and by hand for any season, and uploads `SEASON.tar`
  to a release named `games`
- [x] A test builds 2018 and checks the index against the files

### Notes
- 2026-10-19: first run by hand, for 2018, succeeded in 25 s (7 s building);
  the `games` release's `2018.tar` is byte-identical to a local build. The
  first scheduled run, 2026-10-20 10:00 UTC, is still to check.

## [FBALL-13] Game page on the website

- **Status:** active
- **Priority:** P3
- **Size:** multi
- **Depends on:** FBALL-9, FBALL-11, FBALL-12
- **Tags:** web
- **Commits:** b7f6049

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

The page must credit nflverse, link to CC BY 4.0, and say the data was
changed (FBALL-17). Use the team names and colors, not the logos.

The host's side of FBALL-12 belongs here too, with the nginx route: a cron
line that fetches `SEASON.tar` from the `games` release daily and unpacks
it where nginx serves `/football/`. The files are gzipped only, so the
route needs `gzip_static on` (and `gunzip on` for any client that doesn't
accept gzip).

### Acceptance criteria
- [x] The build's index labels each game's week 1–18, WC, DIV, CONF or SB
- [ ] A page draws a game from its JSON with D3, matching `draw_game`, and
  credits nflverse with a link to CC BY 4.0
- [ ] The page has the filters and paged list described above, and always
  shows a game: `?game=<game_id>`, or else the most recent
- [ ] bennetto.com/football serves the page and the game files, gzipped,
  with the host fetching each season's tarball daily, and a row in
  `DEPLOY.md`; deployed through `publish-site`

## [FBALL-14] Play details on click or hover

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-13
- **Tags:** web
- **Related:** FBALL-17

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
