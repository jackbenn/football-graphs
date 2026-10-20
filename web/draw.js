// Drawing a game from its game_data JSON with D3: the port of draw_game in
// src/football_graphs/plot.py, by play number.

const WIDTH = 1250, HEIGHT = 400;
const MARGIN = {top: 44, right: 12, bottom: 28, left: 34};

// dash pattern for the play that starts at each point, as in plot.py's STYLES
const SOLID = null, DOTTED = '1.5 2.5', DASHED = '6 3', DASHDOT = '8 3 1.5 3';
const STYLES = {run: SOLID, qb_kneel: SOLID, pass: DOTTED, qb_spike: DOTTED,
                kickoff: DASHED, punt: DASHED, field_goal: DASHED, extra_point: DASHED,
                no_play: DASHDOT};
const LEGEND = [['run', SOLID], ['pass', DOTTED], ['kick', DASHED], ['no play (penalty)', DASHDOT]];

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December'];

export function drawGame(svg, game) {
  const {home, away, teams} = game;
  const target = {[home]: 100, [away]: 0};    // the end zone each team drives toward
  const x = d3.scaleLinear([0, game.plays.length + 1], [MARGIN.left, WIDTH - MARGIN.right]);
  const y = d3.scaleLinear([-10, 110], [HEIGHT - MARGIN.bottom, MARGIN.top]);

  svg = d3.select(svg);
  svg.selectAll('*').remove();
  svg.attr('viewBox', `0 0 ${WIDTH} ${HEIGHT}`).attr('class', 'game');

  // yard lines, heavier at the goal lines and midfield, and quarter lines
  svg.append('g').selectAll('line')
    .data(d3.range(0, 101, 10))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', 'black').attr('stroke-width', d => d % 50 === 0 ? 0.5 : 0.3);
  // quarters start between the last play of one and the first of the next
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', y.range()[0]).attr('y2', y.range()[1])
    .attr('stroke', 'black').attr('stroke-width', q => q.quarter === 3 ? 1.5 : 1);

  svg.append('g').selectAll('line')
    .data(game.segments)
    .join('line')
    .attr('x1', s => x(s.play[0])).attr('x2', s => x(s.play[1]))
    .attr('y1', s => y(s.y[0])).attr('y2', s => y(s.y[1]))
    .attr('stroke', s => s.color).attr('stroke-width', 1)
    .attr('stroke-dasharray', s => STYLES[s.play_type] ?? SOLID);

  const symbols = {kickoff: d3.symbol(d3.symbolStar, 110),
                   first_down: d3.symbol(d3.symbolCircle, 36),
                   play: d3.symbol(d3.symbolCircle, 6)};
  svg.append('g').selectAll('path')
    .data(game.plays)
    .join('path')
    .attr('d', p => symbols[p.kind]())
    .attr('transform', p => `translate(${x(p.play)},${y(p.y)})`)
    .attr('fill', p => p.color);

  svg.append('g').selectAll('text')
    .data(game.labels)
    .join('text')
    .attr('x', l => x(l.play)).attr('y', l => y(1.1 * (target[l.team] - 50) + 50))
    .attr('fill', l => teams[l.team].color).attr('class', 'score')
    .text(l => l.score);

  // each team's name in the end zone it defends
  svg.append('g').selectAll('text')
    .data([[home, -5], [away, 105]])
    .join('text')
    .attr('x', x.range()[0] + 5).attr('y', ([, yards]) => y(yards))
    .attr('dominant-baseline', 'central')
    .attr('fill', ([team]) => teams[team].color).attr('class', 'team')
    .text(([team]) => teams[team].nick);

  // axes: quarters along the bottom, yards up the side
  const quarters = game.quarters;
  svg.append('g')
    .attr('transform', `translate(0,${y.range()[0]})`)
    .call(d3.axisBottom(x)
      .tickValues(quarters.map(q => q.play))
      .tickFormat((_, i) => quarters[i].quarter <= 4 ? `Q${quarters[i].quarter}` : 'OT'));
  svg.append('g')
    .attr('transform', `translate(${x.range()[0]},0)`)
    .call(d3.axisLeft(y)
      .tickValues(d3.range(-10, 111, 10))
      .tickFormat(d => d < 0 || d > 100 ? '' : 50 - Math.abs(d - 50)));
  svg.append('rect')
    .attr('x', x.range()[0]).attr('y', y.range()[1])
    .attr('width', x.range()[1] - x.range()[0]).attr('height', y.range()[0] - y.range()[1])
    .attr('fill', 'none').attr('stroke', 'black').attr('stroke-width', 0.8);

  const [year, month, day] = game.date.split('-').map(Number);
  svg.append('text')
    .attr('x', (x.range()[0] + x.range()[1]) / 2).attr('y', 16)
    .attr('text-anchor', 'middle').attr('class', 'title')
    .text(`${teams[away].name} at ${teams[home].name}, ${MONTHS[month - 1]} ${day}, ${year}`);

  const legend = svg.append('g')
    .attr('transform', `translate(${x.range()[1]},${MARGIN.top - 8})`)
    .selectAll('g')
    .data(LEGEND.slice().reverse())
    .join('g');
  let right = 0;
  legend.each(function ([label, dash]) {
    const item = d3.select(this);
    const text = item.append('text').attr('class', 'legend').attr('text-anchor', 'end')
      .attr('dominant-baseline', 'central').attr('x', right).text(label);
    const width = text.node().getComputedTextLength();
    item.append('line')
      .attr('x1', right - width - 30).attr('x2', right - width - 6)
      .attr('stroke', 'black').attr('stroke-width', 1).attr('stroke-dasharray', dash);
    right -= width + 46;
  });
}
