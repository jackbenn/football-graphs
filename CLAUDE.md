# football-graphs

How to set up and run the notebook is in `README.md`; the plan is in
`BACKLOG.md`. These are the rules.

- **Work in the notebook with Jack, live.** Jack runs
  `.venv/bin/marimo edit --no-token EDA.py`, normally at
  http://127.0.0.1:2718. Connect with the `marimo-pair` skill and change
  cells through `marimo._code_mode`. Never edit `EDA.py` directly while the
  notebook is open: the kernel rewrites it on save. If no notebook is open,
  ask Jack to start one rather than starting it yourself.
- **The package in `src/football_graphs/` is ordinary files:** edit them
  directly. The notebook reloads a module when it is saved and re-runs the
  cells that use it.
- **Read a cell's code from the kernel just before editing it.** Jack may
  have changed it in the browser since you last looked.
- **Read the diff of `EDA.py` before committing it.** Stray edits from the
  browser get saved too (a `COmm` once got committed). Jack's own new cells
  are his: ask before committing them.
- **The download cell defines only `_` names** so that nothing depends on it
  and it never re-runs on its own. Keep it that way.
- **Check scoring changes against the whole season.** After changing how
  `plot_game` scores, check that every 2018 game ends on its real final
  score (`home_score`, `away_score`), not just the game on screen.
- **The data's quirks**, learned the hard way:
  - On kickoffs `posteam` is the receiving team; on punts it is the kicking
    team.
  - Rows that are not plays have a NaN `play_type`.
  - Timeouts are `no_play` with a NaN `posteam`.
  - Two-point tries are recorded as `pass` or `run`.
  - There are no two-minute-warning rows.
  - For a safety, take the scoring team from `posteam_score_post` against
    `posteam_score`, not from `posteam` or `defteam`.
