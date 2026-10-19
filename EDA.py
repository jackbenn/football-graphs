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
    # Download one season of nflverse play-by-play, and the table of teams, into data/.
    # Every name here starts with _, so no other cell depends on this one, and it
    # only runs when run by hand. Delete a file to fetch a fresh copy.
    import urllib.request as _request
    from pathlib import Path as _Path

    _year = 2018
    _base = 'https://github.com/nflverse/nflverse-data/releases/download'
    for _url in [f'{_base}/pbp/play_by_play_{_year}.csv.gz',
                 f'{_base}/teams/teams_colors_logos.csv']:
        _path = _Path('data') / _url.rsplit('/', 1)[1]
        if _path.exists():
            print(f'{_path} already exists')
        else:
            _request.urlretrieve(_url, _path)
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
def _(pd):
    teams = pd.read_csv('data/teams_colors_logos.csv').set_index('team_abbr')
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
def _():
    def add_time_column(df):
        """Add column for number of seconds into game"""
        df['Time'] = (df.qtr-1)*60*15 + 60*15 - df.quarter_seconds_remaining

    def add_yards_column(df):
        """Add column Position: yards from the end zone the home team defends, so
        the home team always drives from 0 (the bottom of the plot) toward 100 and
        the away team the other way"""
        df['Position'] = df.yardline_100.where(df.defteam == df.home_team, 100 - df.yardline_100)

    return add_time_column, add_yards_column


@app.cell
def _(np):
    def pick_colors(teams, home, away):
        """Choose a line color for each team from its own colors, darkened where
        needed to show on white, and distinct from each other for normal and
        red-green colorblind vision. The away team gives way first."""
        machado = {    # Machado et al. 2009, severity 1.0
            'protan': np.array([[0.152286, 1.052583, -0.204868],
                                [0.114503, 0.786281, 0.099216],
                                [-0.003882, -0.048116, 1.051998]]),
            'deutan': np.array([[0.367322, 0.860646, -0.227968],
                                [0.280085, 0.672501, 0.047413],
                                [-0.011820, 0.042940, 0.968881]]),
        }

        def linear(color):
            rgb = np.array([int(color[i:i+2], 16) for i in (1, 3, 5)]) / 255
            return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

        def oklab(lin):
            lms = np.cbrt(np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                                    [0.2119034982, 0.6806995451, 0.1073969566],
                                    [0.0883024619, 0.2817188376, 0.6299787005]]) @ lin)
            return np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                             [1.9779984951, -2.4285922050, 0.4505937099],
                             [0.0259040371, 0.7827717662, -0.8086757660]]) @ lms

        def difference(c1, c2, cvd=None):
            """OKLab distance x100, optionally as seen with a color vision deficiency"""
            l1, l2 = linear(c1), linear(c2)
            if cvd:
                l1, l2 = np.clip(machado[cvd] @ l1, 0, 1), np.clip(machado[cvd] @ l2, 0, 1)
            return 100 * np.linalg.norm(oklab(l1) - oklab(l2))

        def contrast(color):
            """WCAG contrast ratio against white"""
            return 1.05 / (linear(color) @ [0.2126, 0.7152, 0.0722] + 0.05)

        def usable(team):
            colors = []
            for color in teams.loc[team, ['team_color', 'team_color2', 'team_color3', 'team_color4']].dropna():
                if difference(color, '#ffffff') < 10:    # white, or nearly
                    continue
                rgb = np.array([int(color[i:i+2], 16) for i in (1, 3, 5)])
                while contrast(color) < 3:               # too pale for thin lines on white
                    rgb = (rgb * 0.97).astype(int)
                    color = '#%02x%02x%02x' % tuple(rgb)
                if color not in colors:
                    colors.append(color)
            return colors

        def distinct(c1, c2):
            return (difference(c1, c2) >= 15 and
                    min(difference(c1, c2, 'protan'), difference(c1, c2, 'deutan')) >= 8)

        home_colors, away_colors = usable(home), usable(away)
        # fewest steps from the two primaries first; on a tie the away team gives way
        pairs = sorted(((h, a) for h in range(len(home_colors)) for a in range(len(away_colors))),
                       key=lambda p: (sum(p), p[0]))
        for h, a in pairs:
            if distinct(home_colors[h], away_colors[a]):
                return home_colors[h], away_colors[a]
        return home_colors[0], 'grey'    # no pair works; no current matchup gets here

    return (pick_colors,)


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
def _(np, pd, pick_colors, plt):
    def plot_game(ax, df, teams, x_axis='play'):
        """Plot a game; x_axis is 'time' for game clock or 'play' for play number"""
        home, away = df.home_team.iloc[0], df.away_team.iloc[0]
        home_color, away_color = pick_colors(teams, home, away)
        colors = {home: home_color, away: away_color}
        target = {home: 100, away: 0}    # the end zone each team drives toward
        scores = {home: 0, away: 0}
        # line style for the play that starts at each point
        styles = {'run': '-', 'qb_kneel': '-', 'pass': ':', 'qb_spike': ':',
                  'kickoff': '--', 'punt': '--', 'field_goal': '--', 'extra_point': '--',
                  'no_play': '-.'}
        play = 0
        quarter_starts = {}    # quarter -> play number of its first play
        last = None        # (x, position, play type, color) of the previous play
        last_end = None    # the end zone the previous play ended in, if it did

        labels = {}    # each team's latest score label

        def score(team, points, conversion=False):
            scores[team] += points
            if conversion:    # update the label already at the touchdown
                labels[team].set_text(scores[team])
            else:
                labels[team] = ax.text(x, 1.1*(target[team]-50)+50, scores[team], color=colors[team],
                                       fontweight='bold', fontsize=13)

        for i, row in df.iterrows():
            if pd.isna(row.play_type) or pd.isna(row.posteam):    # not plays; timeouts
                continue
            # posteam is the receiving team on kickoffs; this wants the kicking team
            if row.play_type == 'kickoff':
                offense, defense = row.defteam, row.posteam
            else:
                offense, defense = row.posteam, row.defteam
            play += 1
            quarter_starts.setdefault(row.qtr, play)
            x = row.Time if x_axis == 'time' else play
            color = colors[offense]

            # the line for the previous play: into the end zone it ended in, or else
            # to this play's spot, except that a kickoff starts a new possession
            if last is not None and (last_end is not None or row.play_type != 'kickoff'):
                last_x, last_pos, last_type, last_color = last
                ax.plot([last_x, x], [last_pos, row.Position if last_end is None else last_end],
                        color=last_color, lw=1, ls=styles.get(last_type, '-'))

            if row.play_type == 'kickoff':
                ax.scatter([x], [row.Position], marker="*", s=200, color=color)
            elif row.down == 1:
                ax.scatter([x], [row.Position], marker="o", color=color)
            else:
                ax.scatter([x], [row.Position], marker=".", color=color, lw=0.5)

            # draw scores, and note the end zone the play ended in, if any
            last_end = None
            if row.touchdown == 1:
                # td_team, since the defense can score too (e.g. a fumble return)
                score(row.td_team, 6)
                last_end = target[row.td_team]
            if row.field_goal_result == 'made':
                score(offense, 3)
                last_end = target[offense]
            if row.play_type == 'extra_point':    # good or not, it's kicked at the goal
                last_end = target[offense]
            if row.extra_point_result == 'good':
                score(offense, 1, conversion=True)
            if row.two_point_conv_result == 'success':
                score(offense, 2, conversion=True)
                last_end = target[offense]
            # a safety usually scores for the defense, but for the kicking team when
            # the receiving team gives one up on a return; the score columns say which
            if row.safety == 1:
                scorer = row.posteam if row.posteam_score_post > row.posteam_score else row.defteam
                score(scorer, 2)
                last_end = target[scorer]
            if row.defensive_two_point_conv == 1:
                score(row.defteam, 2)
                last_end = target[row.defteam]

            last = (x, row.Position, row.play_type, color)
        if x_axis == 'time':
            ax.axvline(15*60, color='k', lw=1)             # ends of quarters
            ax.axvline(2*15*60, color='k')
            ax.axvline(3*15*60, color='k', lw=1)
            ax.axvline(28*60, color='grey', lw=0.5)  # two-minute warning
            ax.axvline(58*60, color='grey', lw=0.5)

            xticks = np.array([0, 5, 10, 15, 20, 25, 28]) + np.array([[0], [30]])
            xticks = xticks.flatten() * 60
            ax.set_xticks(xticks)
            ax.set_xticklabels(['Q1', 10, 5, 'Q2', 10, 5, 2, 'Q3', 10, 5, 'Q4', 10, 5, 2])
            ax.set_xlim(0, 60*15*4)
        else:
            # quarters start between the last play of one and the first of the next
            starts = {q: (0 if q == 1 else first - 0.5) for q, first in quarter_starts.items()}
            for q, x in starts.items():
                if q > 1:
                    ax.axvline(x, color='k', lw=1.5 if q == 3 else 1)
            ax.set_xticks(list(starts.values()))
            ax.set_xticklabels([f'Q{q}' if q <= 4 else 'OT' for q in starts])
            ax.set_xlim(0, play + 1)
        for line in range(10, 100, 10):
            ax.axhline(line, color='k', lw=0.3)
        ax.axhline(0, color='k', lw=0.5)
        ax.axhline(100, color='k', lw=0.5)
        ax.axhline(50, color='k', lw=0.5)

        ax.set_yticks(np.arange(-10, 111, 10))
        ax.set_yticklabels(['', 0, 10, 20, 30, 40, 50, 40, 30, 20, 10, 0, ''])

        ax.legend(handles=[plt.Line2D([], [], color='k', lw=1, ls=ls, label=label)
                           for label, ls in [('run', '-'), ('pass', ':'), ('kick', '--'),
                                             ('no play (penalty)', '-.')]],
                  loc='lower right', bbox_to_anchor=(1, 1), ncol=4, frameon=False)

        # each team's name in the end zone it defends
        for team, color, y in [(home, home_color, -5), (away, away_color, 105)]:
            ax.text(0.005, y, teams.team_nick[team], transform=ax.get_yaxis_transform(),
                    color=color, fontweight='bold', fontsize=13, va='center')

        date = pd.Timestamp(df.game_date.iloc[0])
        ax.set_title(f'{teams.team_name[away]} at {teams.team_name[home]}, '
                     f'{date:%B} {date.day}, {date.year}')

        ax.set_ylim(-10, 110)

    return (plot_game,)


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
