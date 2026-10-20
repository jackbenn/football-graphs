"""Turning a game's play-by-play into what a plot of it shows."""

import pandas as pd

from .colors import pick_colors

# the play-by-play columns game_data reads, before add_time_column and
# add_yards_column add theirs
COLUMNS = ['home_team', 'away_team', 'game_date', 'qtr', 'quarter_seconds_remaining',
           'play_type', 'posteam', 'defteam', 'yardline_100', 'down', 'touchdown', 'td_team',
           'field_goal_result', 'extra_point_result', 'two_point_conv_result', 'safety',
           'posteam_score', 'posteam_score_post', 'defensive_two_point_conv']


def game_data(df, teams):
    """What a plot of the game shows, as plain data that can be saved as JSON:
    the teams, a line segment for each play, a marker at the start of each play,
    the score labels, and where each quarter starts. Every point has both an x
    for the play number (`play`) and one for the game clock (`time`), and a `y`
    from add_yards_column."""
    home, away = df.home_team.iloc[0], df.away_team.iloc[0]
    home_color, away_color = pick_colors(teams, home, away)
    colors = {home: home_color, away: away_color}
    target = {home: 100, away: 0}    # the end zone each team drives toward
    scores = {home: 0, away: 0}
    segments, markers, labels = [], [], []
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
        markers.append(dict(point, y=float(row.Position), kind=kind, color=color))

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

        last = dict(point, y=float(row.Position), play_type=row.play_type, color=color)

    date = pd.Timestamp(df.game_date.iloc[0])
    return {
        'home': home,
        'away': away,
        'teams': {team: {'name': teams.team_name[team], 'nick': teams.team_nick[team],
                         'color': colors[team]}
                  for team in (home, away)},
        'date': date.strftime('%Y-%m-%d'),
        'segments': segments,
        'markers': markers,
        'labels': labels,
        # quarters start between the last play of one and the first of the next
        'quarters': [{'quarter': q, 'play': 0 if q == 1 else first - 0.5, 'time': (q-1)*15*60}
                     for q, first in quarter_starts.items()],
        'plays': play,
        'final_score': scores,
    }
