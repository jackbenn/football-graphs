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
- A kickoff called back by a penalty is a `no_play` with the receiving team
  as `posteam`, so it is drawn as an ordinary play in the receiving team's
  color, not a star in the kicking team's. There are 13 in 2018, including
  the opening kickoff of 2018102500; `kickoff_attempt` marks them.

### Acceptance criteria
- [ ] Each fix above is visible on the 2018090902 game and on one game whose
  first play isn't at x=0
- [ ] Every 2018 game still ends on its real final score

## [FBALL-12] Download the data and build the game files on a schedule

- **Status:** idea
- **Priority:** P3
- **Size:** session
- **Depends on:** FBALL-9, FBALL-11
- **Tags:** data, infra
- **Related:** FBALL-18

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

Still open: GitHub disables scheduled workflows in a public repo after 60
days without activity, which the off-season exceeds. Re-enable it by hand
each August, or have the workflow keep itself alive.

A change to the JSON format means rebuilding every season's files, so the
build should be one command that FBALL-18 can run for any season.

## [FBALL-13] Game page on the website

- **Status:** idea
- **Priority:** P3
- **Size:** multi
- **Depends on:** FBALL-9, FBALL-11, FBALL-12
- **Tags:** web

A page at bennetto.com/football where a visitor selects a game through some
controls and sees its graph, drawn in the browser with D3 from the game's
precomputed JSON (FBALL-11). The work is porting `draw_game` to D3, the
controls, and the deployment: adding this repo as a submodule of
`bennetto-infra`, an nginx route for `/football/` serving the page and the
JSON as static files, and a row in `DEPLOY.md`, following `gengo` and
`taking_the_story`. There is no app server, so it may not need a container
of its own, only files nginx can reach. Deployed through the `publish-site`
skill.

Still to decide: how a visitor picks a game (season, week, team).

The page must credit nflverse, link to CC BY 4.0, and say the data was
changed (FBALL-17). Use the team names and colors, not the logos.

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
