# Backlog — football-graphs

Prefix: FBALL · Next ID: 6 · Schema: v1

A visualization of an American football game: one axis shows the position of
the ball, the other time, either clock time or the play number. So far there
is play-by-play data for 2018 and one notebook experimenting with plots of a
single game.

## [FBALL-1] Collaborate with Claude inside the notebook

- **Status:** idea
- **Priority:** unknown
- **Size:** session
- **Depends on:** none
- **Tags:** exploration
- **Related:** FBALL-5

Use this project as an exercise in working with Claude inside a notebook,
before improving the visualization itself.

Open questions to settle when refining it:
- Where the collaboration happens: Jupyter, VS Code, or Claude Code editing
  the `.ipynb` directly.
- How Claude sees results. Outputs exist only after the cells are run, so
  either Jack runs them and Claude reads the saved notebook, or Claude
  executes it itself.
- Whether outputs stay in git at all (FBALL-5).

## [FBALL-2] Declare the dependencies

- **Status:** idea
- **Priority:** unknown
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

- **Status:** idea
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** data

Cell 4 of `EDA.ipynb` loads `pbp-2014.csv` through `pbp-2018.csv` from
`data/`, but only `pbp-2018.csv` is in the repo, so the notebook fails on a
fresh clone. The plotting uses a single 2018 game (`GameId` 2018090902). Either
load only 2018, or get the other years and say where they come from. Whether
nflsavant.com still serves them is unchecked. Found by `project-init`
(META-1), 2026-10-19.

## [FBALL-5] Keep the notebook's outputs out of git, or small

- **Status:** idea
- **Priority:** unknown
- **Size:** quick
- **Depends on:** none
- **Tags:** config
- **Related:** FBALL-1

`EDA.ipynb` is 2.2 MB, of which 5.6 KB is code and markdown; the rest is
output, mostly whole DataFrames displayed with `pd.options.display.max_rows =
None`. One commit (`b242572`) was a 53,000-line diff. Options: stop displaying
whole frames, strip outputs on commit (`nbstripout`), or pair the notebook
with a script (`jupytext`). Matters for FBALL-1, since a collaborator reads
and diffs the notebook. Found by `project-init` (META-1), 2026-10-19.
