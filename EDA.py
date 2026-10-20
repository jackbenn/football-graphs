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

    from football_graphs.data import add_time_column, add_yards_column, load_season, load_teams
    from football_graphs.plot import plot_game

    return (
        add_time_column,
        add_yards_column,
        load_season,
        load_teams,
        pd,
        plot_game,
        plt,
    )


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
    # Download one season of nflverse play-by-play, and the table of teams, into data/.
    # Every name here starts with _, so no other cell depends on this one, and it
    # only runs when run by hand. Delete a file to fetch a fresh copy.
    from football_graphs.data import download as _download

    _year = 2018
    _download(_year)
    return


@app.cell
def _(load_season, pd):
    full_df = pd.concat([load_season(year) for year in [2018]], axis=0)
    return (full_df,)


@app.cell
def _(load_teams):
    teams = load_teams()
    return (teams,)


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
def _(df, plot_game, plt, teams):
    fig, ax = plt.subplots(figsize=(25,8))
    plot_game(ax, df, teams)
    fig
    return


@app.cell
def _(df, plot_game, plt, teams):
    _fig, _ax = plt.subplots(figsize=(25,8))
    plot_game(_ax, df, teams, x_axis='time')
    _fig
    return


if __name__ == "__main__":
    app.run()
