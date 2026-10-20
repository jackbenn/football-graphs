"""Drawing a game."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .game import game_data

# line style for the play that starts at each point
STYLES = {'run': '-', 'qb_kneel': '-', 'pass': ':', 'qb_spike': ':',
          'kickoff': '--', 'punt': '--', 'field_goal': '--', 'extra_point': '--',
          'no_play': '-.'}


def plot_game(ax, df, teams, x_axis='play'):
    """Plot a game; x_axis is 'time' for game clock or 'play' for play number"""
    draw_game(ax, game_data(df, teams), x_axis)


def draw_game(ax, game, x_axis='play'):
    """Draw a game from game_data; x_axis is 'time' for game clock or 'play' for
    play number"""
    home, away, teams = game['home'], game['away'], game['teams']
    target = {home: 100, away: 0}    # the end zone each team drives toward

    for segment in game['segments']:
        ax.plot(segment[x_axis], segment['y'], color=segment['color'], lw=1,
                ls=STYLES.get(segment['play_type'], '-'))
    for marker in game['markers']:
        if marker['kind'] == 'kickoff':
            ax.scatter([marker[x_axis]], [marker['y']], marker="*", s=200, color=marker['color'])
        elif marker['kind'] == 'first_down':
            ax.scatter([marker[x_axis]], [marker['y']], marker="o", color=marker['color'])
        else:
            ax.scatter([marker[x_axis]], [marker['y']], marker=".", color=marker['color'], lw=0.5)
    for label in game['labels']:
        team = label['team']
        ax.text(label[x_axis], 1.1*(target[team]-50)+50, label['score'], color=teams[team]['color'],
                fontweight='bold', fontsize=13)

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
        starts = {quarter['quarter']: quarter['play'] for quarter in game['quarters']}
        for q, x in starts.items():
            if q > 1:
                ax.axvline(x, color='k', lw=1.5 if q == 3 else 1)
        ax.set_xticks(list(starts.values()))
        ax.set_xticklabels([f'Q{q}' if q <= 4 else 'OT' for q in starts])
        ax.set_xlim(0, game['plays'] + 1)
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
    for team, y in [(home, -5), (away, 105)]:
        ax.text(0.005, y, teams[team]['nick'], transform=ax.get_yaxis_transform(),
                color=teams[team]['color'], fontweight='bold', fontsize=13, va='center')

    date = pd.Timestamp(game['date'])
    ax.set_title(f"{teams[away]['name']} at {teams[home]['name']}, "
                 f'{date:%B} {date.day}, {date.year}')

    ax.set_ylim(-10, 110)
