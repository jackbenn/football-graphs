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
