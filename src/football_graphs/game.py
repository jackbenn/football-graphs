"""Turning a game's play-by-play into what a plot of it shows."""

import pandas as pd

from .colors import pick_colors

# the play-by-play columns game_data reads, before add_time_column and
# add_yards_column add theirs
COLUMNS = ['game_id', 'home_team', 'away_team', 'game_date', 'qtr', 'quarter_seconds_remaining',
           'play_type', 'posteam', 'defteam', 'yardline_100', 'down', 'touchdown', 'td_team',
           'field_goal_result', 'extra_point_result', 'two_point_conv_result', 'safety',
           'posteam_score', 'posteam_score_post', 'defensive_two_point_conv', 'ydstogo', 'desc',
           'timeout', 'timeout_team', 'incomplete_pass', 'out_of_bounds', 'penalty', 'interception',
           'fumble_lost', 'fourth_down_failed']


def late(quarter, clock):
    """Whether the clock stops for good when a play goes out of bounds: in the
    last two minutes of the first half, or the last five of the second half or
    of overtime. Earlier, it restarts when the ball is ready for play, so the
    clock is taken as running."""
    return clock <= (120 if quarter == 2 else 300 if quarter >= 4 else -1)


def clock_stop(row):
    """What stopped the clock after a play, as far as the play's own columns tell:
    the first that applies of a score (or a try after a touchdown), a turnover, a
    kick, an incomplete pass, a penalty (such as one that cancels an incomplete
    pass, or an offside before the snap), and going out of bounds late in a half;
    else 'running'. add_clock_stops puts a timeout, the two-minute warning and
    the end of a quarter ahead of these."""
    if (row.touchdown == 1 or row.field_goal_result == 'made' or row.safety == 1
            or row.play_type == 'extra_point' or pd.notna(row.two_point_conv_result)):
        return 'score'
    if row.interception == 1 or row.fumble_lost == 1 or row.fourth_down_failed == 1:
        return 'turnover'
    if row.play_type in ('kickoff', 'punt', 'field_goal'):
        return 'kick'
    if row.incomplete_pass == 1:    # spikes too
        return 'incomplete'
    if row.penalty == 1:
        return 'penalty'
    if row.out_of_bounds == 1 and late(row.qtr, row.quarter_seconds_remaining):
        return 'out_of_bounds'
    return 'running'


def game_data(df, teams):
    """What a plot of the game shows, as plain data that can be saved as JSON:
    the teams, each play (where its marker goes, and its details: the clock, down
    and distance, description, the score after it, any timeouts called after it,
    and how many seconds of game clock it took and what stopped the clock, as in
    add_clock_stops), a line segment for each play, the score labels, and where
    each quarter starts. Every point has both an x for the play number (`play`)
    and one for the game clock in seconds (`time`), and a `y` from
    add_yards_column."""
    home, away = df.home_team.iloc[0], df.away_team.iloc[0]
    home_color, away_color = pick_colors(teams, home, away)
    colors = {home: home_color, away: away_color}
    target = {home: 100, away: 0}    # the end zone each team drives toward
    scores = {home: 0, away: 0}
    segments, plays, labels = [], [], []
    play = 0
    quarter_starts = {}    # quarter -> play number of its first play
    last = None        # the point and color of the previous play, and its type
    last_end = None    # the end zone the previous play ended in, if it did

    def score(team, points, conversion=False):
        scores[team] += points
        if conversion:    # update the label already at the touchdown
            next(label for label in reversed(labels) if label['team'] == team)['score'] = scores[team]
        else:
            labels.append(dict(point, team=team, score=scores[team]))

    for i, row in df.iterrows():
        # a timeout is its own row, or else on the play it follows, such as a lost challenge
        if row.timeout == 1 and plays and not (pd.notna(row.play_type) and pd.notna(row.posteam)):
            plays[-1]['timeouts'].append(row.timeout_team)
        if pd.isna(row.play_type) or pd.isna(row.posteam):    # not plays; timeouts
            continue
        # posteam is the receiving team on kickoffs; this wants the kicking team
        if row.play_type == 'kickoff':
            offense, defense = row.defteam, row.posteam
        else:
            offense, defense = row.posteam, row.defteam
        play += 1
        quarter_starts.setdefault(int(row.qtr), play)
        point = {'play': play, 'time': float(row.Time)}
        color = colors[offense]

        # the line for the previous play: into the end zone it ended in, or else
        # to this play's spot, except that a kickoff starts a new possession
        if last is not None and (last_end is not None or row.play_type != 'kickoff'):
            end = float(row.Position) if last_end is None else last_end
            segments.append({'play': [last['play'], play], 'time': [last['time'], point['time']],
                             'y': [last['y'], end], 'play_type': last['play_type'],
                             'color': last['color']})

        if row.play_type == 'kickoff':
            kind = 'kickoff'
        elif row.down == 1:
            kind = 'first_down'
        else:
            kind = 'play'
        plays.append(dict(point, y=float(row.Position), kind=kind, color=color, offense=offense,
                          play_type=row.play_type, quarter=int(row.qtr),
                          clock=int(row.quarter_seconds_remaining),
                          down=None if pd.isna(row.down) else int(row.down),
                          distance=None if pd.isna(row.down) else int(row.ydstogo),
                          desc=row.desc, timeouts=[], stop=clock_stop(row)))

        # scores, and the end zone the play ended in, if any
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

        plays[-1]['score'] = dict(scores)    # after the play, conversions included
        if row.timeout == 1:
            plays[-1]['timeouts'].append(row.timeout_team)
        last = dict(point, y=float(row.Position), play_type=row.play_type, color=color)

    add_clock_stops(plays, df.groupby('qtr').Time.max())

    date = pd.Timestamp(df.game_date.iloc[0])
    return {
        'home': home,
        'away': away,
        'teams': {team: {'name': teams.team_name[team], 'nick': teams.team_nick[team],
                         'color': colors[team]}
                  for team in (home, away)},
        'date': date.strftime('%Y-%m-%d'),
        'segments': segments,
        'plays': plays,
        'labels': labels,
        # quarters start between the last play of one and the first of the next
        'quarters': [{'quarter': q, 'play': 0 if q == 1 else first - 0.5, 'time': (q-1)*15*60}
                     for q, first in quarter_starts.items()],
        'final_score': scores,
    }


def add_clock_stops(plays, period_ends):
    """Give each play its `duration`, the seconds of game clock from its snap to
    the next one, or to the end of its period (from period_ends, the game time
    at which each period ends) for the last play of one. Settle its `stop`, what
    stopped the clock after it: the end of the quarter, the two-minute warning, or
    a timeout, ahead of the reason clock_stop gave it.

    A few plays are out of order in the data (46 in 2018), so that the clock runs
    backwards, even into the quarter before; their duration is None."""
    for play, after in zip(plays, plays[1:] + [None]):
        if after is None or after['quarter'] > play['quarter']:
            play['duration'] = float(period_ends[play['quarter']]) - play['time']
            play['stop'] = 'quarter_end'
            continue
        duration = after['time'] - play['time']
        play['duration'] = duration if duration >= 0 else None
        if play['duration'] is None:
            continue
        if play['quarter'] in (2, 4, 5, 6) and play['clock'] > 120 >= after['clock']:
            play['stop'] = 'two_minute_warning'
        elif play['timeouts']:
            play['stop'] = 'timeout'
