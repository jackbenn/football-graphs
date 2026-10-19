import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # EDA on football stats

    There's a lot of EDA here understanding the format, so I'm starting with a notebook.

    The data is nflverse play-by-play (https://github.com/nflverse/nflverse-data), downloaded
    by the cell below. It originally came from http://nflsavant.com/, in an older format.
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    return np, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We have some big dataframes and we need to see the whole things. I'm not sure if this is necessary on marimo.
    """)
    return


@app.cell
def _(pd):
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.max_colwidth = 200
    return


@app.cell
def _():
    # Download one season of nflverse play-by-play into data/.
    # Every name here starts with _, so no other cell depends on this one, and it
    # only runs when run by hand. Delete the file to fetch a fresh copy.
    import urllib.request as _request
    from pathlib import Path as _Path

    _year = 2018
    _path = _Path(f'data/play_by_play_{_year}.csv.gz')
    if _path.exists():
        print(f'{_path} already exists')
    else:
        _request.urlretrieve(
            f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{_year}.csv.gz',
            _path)
        print(f'downloaded {_path}')
    return


@app.cell
def _(pd):
    yearly_df = []
    for year in [2018]:
        yearly_df.append(pd.read_csv(f'data/play_by_play_{year}.csv.gz', low_memory=False))
    full_df = pd.concat(yearly_df, axis=0)
    return (full_df,)


@app.cell
def _(full_df):
    full_df.shape
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's look at all the data for one game, sorted by time.
    """)
    return


@app.cell
def _(full_df):
    full_df[full_df.old_game_id==2018090902].sort_values('play_id').head(10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Fifth quarter is probably overtime, so that will need to be considered in the graph.
    """)
    return


@app.cell
def _(full_df):
    full_df.qtr.value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Rows that aren't plays have a NaN play_type: the start of each game (a row whose
    description starts with `GAME`), end of quarter/half/game, and a few others such as
    lightning delays and declined pre-snap penalties. Only some of them have a NaN posteam.

    Timeouts have play_type `no_play` and a NaN posteam. There are no rows for the
    two-minute warning.

    On kickoffs, posteam is the receiving team, not the kicking team.
    """)
    return


@app.cell
def _(full_df):
    full_df[full_df.play_type.isna()].desc.value_counts().head(10)
    return


@app.cell
def _(full_df):
    full_df[full_df.posteam.isna() &
            full_df.play_type.notna() &
            ~full_df.desc.str.startswith('Timeout')]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's start graphing!
    """)
    return


@app.cell
def _(add_time_column, add_yards_column, full_df):
    #df = full_df[full_df.old_game_id==2018090900].sort_values('play_id').reset_index(drop=True)
    df = full_df[full_df.old_game_id==2018090902].sort_values('play_id').reset_index(drop=True)
    add_time_column(df)
    add_yards_column(df)
    return (df,)


@app.cell
def _():
    def add_time_column(df):
        """Add column for number of seconds into game"""
        df['Time'] = (df.qtr-1)*60*15 + 60*15 - df.quarter_seconds_remaining

    # this hardcoding is really bad
    def add_yards_column(df, team1 = 'IND'):
        """Add column Position: yards from the end zone team1 attacks, so team1
        always drives toward 0 and the other team toward 100"""
        df['Position'] = df.yardline_100.where(df.defteam != team1, 100 - df.yardline_100)

    return add_time_column, add_yards_column


@app.cell
def _(df):
    df.head(10)
    return


@app.cell
def _(df):
    df[['posteam', 'defteam', 'play_type', 'down', 'side_of_field', 'yardline_100', 'yards_gained', 'desc']]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are a bunch of play types; we should handle all...eventually.
    """)
    return


@app.cell
def _(df):
    df.play_type.value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The field_goal_result column says whether a field goal was good.
    """)
    return


@app.cell
def _(df):
    df[df.play_type == 'field_goal'][['Time', 'posteam', 'kick_distance', 'field_goal_result', 'desc']]
    return


@app.cell
def _(last_color, np, pd):
    def plot_game(ax, df):
        last_pos = None
        last_time = None
        last_type = None
        scores = [0,0]
        for i, row in df.iterrows():
            if pd.isna(row.play_type) or pd.isna(row.posteam):    # not plays; timeouts
                continue
            # posteam is the receiving team on kickoffs; this wants the kicking team
            if row.play_type == 'kickoff':
                offense, defense = row.defteam, row.posteam
            else:
                offense, defense = row.posteam, row.defteam
            #TODO fix this
            index = 0 if defense == 'IND' else 1
            endzone = 100 if defense == 'IND' else 0
            # to do: add Color to df
            color = 'r' if offense == 'IND' else 'b'

            if row.play_type == 'kickoff':
                ax.scatter([row.Time], [row.Position], marker="*", s=300, color=color)
                if last_type is not None:
                    ax.plot([last_time, row.Time], [last_pos, endzone], color=last_color, lw=0.5)
            else:
                if row.down == 1:
                    ax.scatter([row.Time], [row.Position], marker="o", color=color)
                else:
                    ax.scatter([row.Time], [row.Position], marker=".", color=color, lw=0.5)
                ax.plot([last_time, row.Time], [last_pos, row.Position], color=last_color, lw=0.5)

            # draw scores
            if row.touchdown == 1:
                # need ot handle extra point(s)
                scores[index] += 7
                ax.text(row.Time, 1.1*(endzone-50)+50, scores[index], fontweight='bold')
            if row.field_goal_result == 'made':
                scores[index] += 3
                ax.text(row.Time, 1.1*(endzone-50)+50, scores[index], fontweight='bold')

            last_time = row.Time
            last_pos = row.Position
            last_type = row.play_type
            last_color = color
        ax.axvline(15*60, color='k', lw=1)             # ends of quarters
        ax.axvline(2*15*60, color='k')
        ax.axvline(3*15*60, color='k', lw=1)
        ax.axvline(28*60, color='grey', lw=0.5)  # two-minute warning
        ax.axvline(58*60, color='grey', lw=0.5)
        for line in range(10, 100, 10):
            ax.axhline(line, color='k', lw=0.3)
        ax.axhline(0, color='k', lw=0.5)
        ax.axhline(100, color='k', lw=0.5)
        ax.axhline(50, color='k', lw=0.5)

        xticks = np.array([0, 5, 10, 15, 20, 25, 28]) + np.array([[0], [30]])
        xticks = xticks.flatten() * 60
        ax.set_xticks(xticks)
        ax.set_xticklabels(['Q1', 10, 5, 'Q2', 10, 5, 2, 'Q3', 10, 5, 'Q4', 10, 5, 2])
        ax.set_yticks(np.arange(-10, 111, 10))
        ax.set_yticklabels(['', 0, 10, 20, 30, 40, 50, 40, 30, 20, 10, 0, ''])

        ax.set_xlim(0, 60*15*4)
        ax.set_ylim(-10, 110)

    return (plot_game,)


@app.cell
def _(df, plot_game, plt):
    fig, ax = plt.subplots(figsize=(25,8))
    plot_game(ax, df)
    fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
