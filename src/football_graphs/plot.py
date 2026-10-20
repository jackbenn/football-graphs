"""Drawing a game."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .colors import pick_colors


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
