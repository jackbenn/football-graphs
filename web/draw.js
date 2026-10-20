// Drawing a game from its game_data JSON with D3: the port of draw_game in
// src/football_graphs/plot.py, by play number, and below it a bar for each play
// of the clock time it took, colored by what stopped the clock.

const WIDTH = 1250, GAME_HEIGHT = 400, HEIGHT = 500;
const MARGIN = {top: 44, right: 34, bottom: 28, left: 34};
const CLOCK = {top: 412, bottom: 492, most: 60};    // the clock panel, in pixels, and its top in seconds

// dash pattern for the play that starts at each point, as in plot.py's STYLES
const SOLID = null, DOTTED = '1.5 2.5', DASHED = '6 3', DASHDOT = '8 3 1.5 3';
const STYLES = {run: SOLID, qb_kneel: SOLID, pass: DOTTED, qb_spike: DOTTED,
                kickoff: DASHED, punt: DASHED, field_goal: DASHED, extra_point: DASHED,
                no_play: DASHDOT};
const LEGEND = [['run', SOLID], ['pass', DOTTED], ['kick', DASHED], ['penalty', DASHDOT]];

// what stopped the clock after each play, in groups of like reasons with like
// colors, as the legend shows them: game_data's reasons, with the kicks and
// turnovers together as changes of possession, and the two-minute warning with
// the end of the quarter
const STOPS = [
  [{label: 'clock kept running', color: '#c2c0ba', stops: ['running']},
   {label: 'change of possession', color: '#7a7871', stops: ['kick', 'turnover']}],
  [{label: 'incomplete pass', color: '#1c5cab', stops: ['incomplete']},
   {label: 'out of bounds', color: '#6da7ec', stops: ['out_of_bounds']}],
  [{label: 'timeout', color: '#d95926', stops: ['timeout']},
   {label: 'two-minute warning or end of quarter', color: '#e87ba4',
    stops: ['two_minute_warning', 'quarter_end']},
   {label: 'penalty', color: '#eda100', stops: ['penalty']}],
  [{label: 'score', color: '#199e70', stops: ['score']}],
];
const STOP = Object.fromEntries(STOPS.flat().flatMap(item => item.stops.map(stop => [stop, item])));

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December'];

export function drawGame(svg, game) {
  const {home, away, teams} = game;
  const target = {[home]: 100, [away]: 0};    // the end zone each team drives toward
  // a play's room either side of the first and last, so their markers clear the frame
  const x = d3.scaleLinear([-1, game.plays.length + 2], [MARGIN.left, WIDTH - MARGIN.right]);
  const y = d3.scaleLinear([-10, 110], [GAME_HEIGHT - MARGIN.bottom, MARGIN.top]);

  svg = d3.select(svg);
  svg.selectAll('*').remove();
  svg.attr('viewBox', `0 0 ${WIDTH} ${HEIGHT}`).attr('class', 'game');

  // yard lines, darker at the goal lines and midfield, and quarter lines, which
  // stop at the goal lines to leave the end zones to the score labels
  svg.append('g').selectAll('line')
    .data(d3.range(0, 101, 10))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', d => d % 50 === 0 ? '#999' : '#ddd').attr('shape-rendering', 'crispEdges');
  // quarters start between the last play of one and the first of the next
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', y(0)).attr('y2', y(100))
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
    .attr('fill', l => teams[l.team].color).attr('class', 'score').attr('text-anchor', 'middle')
    .text(l => l.score);

  // each team's name in the end zone it defends
  svg.append('g').selectAll('text')
    .data([[home, -5], [away, 105]])
    .join('text')
    .attr('x', x.range()[0] + 5).attr('y', ([, yards]) => y(yards))
    .attr('dominant-baseline', 'central')
    .attr('fill', ([team]) => teams[team].color).attr('class', 'team')
    .text(([team]) => teams[team].nick);

  // axes: quarters along the bottom, the first at the frame, and yards up both
  // sides, with no ticks at the backs of the end zones
  const quarters = game.quarters;
  svg.append('g')
    .attr('transform', `translate(0,${y.range()[0]})`)
    .call(d3.axisBottom(x)
      .tickSizeOuter(0)
      .tickValues(quarters.map(q => q.quarter === 1 ? x.domain()[0] : q.play))
      .tickFormat((_, i) => quarters[i].quarter <= 4 ? `Q${quarters[i].quarter}` : 'OT'));
  const yards = axis => axis(y)
    .tickSizeOuter(0)
    .tickValues(d3.range(0, 101, 10))
    .tickFormat(d => 50 - Math.abs(d - 50));
  svg.append('g').attr('transform', `translate(${x.range()[0]},0)`).call(yards(d3.axisLeft));
  svg.append('g').attr('transform', `translate(${x.range()[1]},0)`).call(yards(d3.axisRight));
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

  drawClock(svg, game, x);
}

// a bar for each play of the clock time it took, up to CLOCK.most seconds, in
// the color of what stopped the clock, with the quarters marked as above
function drawClock(svg, game, x) {
  const y = d3.scaleLinear([0, CLOCK.most], [CLOCK.bottom, CLOCK.top]).clamp(true);
  const width = Math.max(1, x(1) - x(0) - 1.5);

  svg.append('g').selectAll('line')
    .data(y.ticks(3).filter(d => d > 0))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', '#ddd').attr('shape-rendering', 'crispEdges');
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', CLOCK.bottom).attr('y2', CLOCK.top)
    .attr('stroke', 'black').attr('stroke-width', q => q.quarter === 3 ? 1.5 : 1);

  const clock = seconds => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  svg.append('g').selectAll('rect')
    .data(game.plays.filter(p => p.duration !== null))
    .join('rect')
    .attr('x', p => x(p.play) - width / 2).attr('width', width)
    .attr('y', p => y(p.duration)).attr('height', p => CLOCK.bottom - y(p.duration))
    .attr('fill', p => STOP[p.stop].color)
    .append('title')
    .text(p => `${p.quarter <= 4 ? `Q${p.quarter}` : 'OT'} ${clock(p.clock)}: ` +
               `${p.duration} seconds, ${STOP[p.stop].label}`);

  svg.append('g')
    .attr('transform', `translate(${x.range()[0]},0)`)
    .call(d3.axisLeft(y)
      .tickSizeOuter(0)
      .ticks(3)
      .tickFormat(d => d === 0 ? '' : clock(d)));
  svg.append('rect')
    .attr('x', x.range()[0]).attr('y', CLOCK.top)
    .attr('width', x.range()[1] - x.range()[0]).attr('height', CLOCK.bottom - CLOCK.top)
    .attr('fill', 'none').attr('stroke', 'black').attr('stroke-width', 0.8);
}

// the legend for the clock bars, into an HTML element: what stopped the clock,
// one item to a line, in its groups
export function drawClockLegend(element) {
  const group = d3.select(element).selectAll('ul').data(STOPS).join('ul');
  const item = group.selectAll('li').data(items => items).join('li');
  item.append('span').attr('class', 'swatch').style('background', item => item.color);
  item.append('span').text(item => item.label);
}
