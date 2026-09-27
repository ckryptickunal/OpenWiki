const BPM = 120;
const beat = (n) => n * 60 / BPM;            // quarter notes
const bar = (n) => beat(4 * n);              // 4/4 bars

// The Founder Book link graph (real data, see Marketing/launch-video/FACTS.md), drawn by scene "wiki".
const G = window.GRAPH;
const GR = new Float32Array(G.n);
for (let i = 0; i < G.n; i++) GR[i] = Math.hypot(G.x[i], G.y[i]) / 1000;
const GSIZE = G.d.map((d) => 0.85 + Math.sqrt(d) * 0.24);
const GP = new Float32Array(G.n * 2);
const GRAPH_T0 = beat(24.75);
function drawGraph(c, t, q, K) {
  const tau = t - GRAPH_T0;
  if (tau <= 0) return;
  const reveal = K.S(tau, [1, 5.2]) * 1.06;            // centre-out bloom, no overshoot
  const edges = K.S(tau - 0.35, [1, 4.4]);
  const rot = -0.16 + 0.16 * K.S(tau, [1, 3.4]);
  const zoom = 0.9 + 0.1 * K.S(tau, [1, 3.4]);
  const CXg = 1484, CYg = 540, RAD = 330 * zoom;
  const cs = Math.cos(rot), sn = Math.sin(rot);
  for (let i = 0; i < G.n; i++) {
    const x = G.x[i] / 1000, y = G.y[i] / 1000;
    GP[2 * i] = CXg + (x * cs - y * sn) * RAD; GP[2 * i + 1] = CYg + (x * sn + y * cs) * RAD;
  }
  if (edges > 0.002) {
    c.globalAlpha = 0.09 * edges; c.strokeStyle = K.col('accent'); c.lineWidth = 0.7; c.beginPath();
    for (let k = 0; k < G.e.length; k += 2) {
      const a = G.e[k], b = G.e[k + 1];
      if (GR[a] > reveal || GR[b] > reveal) continue;
      c.moveTo(GP[2 * a], GP[2 * a + 1]); c.lineTo(GP[2 * b], GP[2 * b + 1]);
    }
    c.stroke();
  }
  const cols = ['fg', 'accent', 'ember'];
  for (let ty = 0; ty < 3; ty++) {
    c.globalAlpha = 1; c.fillStyle = K.col(cols[ty]); c.beginPath();
    for (let i = 0; i < G.n; i++) {
      if (G.t[i] !== ty) continue;
      const k = (reveal - GR[i]) / 0.07;
      if (k <= 0) continue;
      const r = GSIZE[i] * Math.min(1, k) * (0.9 + 0.1 * zoom);
      c.moveTo(GP[2 * i] + r, GP[2 * i + 1]); c.arc(GP[2 * i], GP[2 * i + 1], r, 0, Math.PI * 2);
    }
    c.fill();
  }
  c.globalAlpha = 1;
}

// Optical pairs for tight display tracking (values from the critique's ink-gap check).
const PAIRS = { at: 8, st: 10, ta: 9, pe: 19, Wi: 19, ki: 27, ed: 16, 't.': 10, sa: 10, fi: 10, AI: 10, rt: 32, ts: 24, co: 15, es: 16, ce: 11, wi: 16, wn: 16, re: 8, ss: 21 };
const H1 = 152;                                // headline cap height, px
const B1 = 416, B2 = 632;                      // two-line stack baselines
const C1 = 760, C2 = 824;                      // crumb baselines
const enterA = (at) => ({ at, from: 120, spring: 'LAND', blur: 14, stagger: 32 });
const out = (at) => ({ at, dy: -1100, spring: 'EXIT', stagger: 64 });

const FILM = {
  title: 'OpenWiki launch film',
  alt: 'You watched it. You saved it. You can’t find it. Your AI starts over. OpenWiki compiles it once. A wiki you own. You find the moment. Your AI reads less. OpenWiki. github.com/ckryptickunal/OpenWiki. Free and open source, MIT.',
  W: 1920, H: 1080, FPS: 60, DUR: bar(13), BPM,
  palette: { bg: '#15100C', fg: '#FAF6F2', accent: '#F5C451', ember: '#E5895A', muted: '#B3A293' },
  misPair: ['accent', 'ember'],
  misAlpha: 0.4,
  smearColor: 'accent',
  scrambleColor: 'accent',
  fonts: {
    display: { family: 'Inter Display', weight: 700 },
    label: { family: 'Inter Display', weight: 600 },
    mono: { family: 'JetBrains Mono', weight: 500 },
  },
  grid: { margin: 128, unit: 8 },
  mono: { size: 44, track: 0 },
  poster: 0,
  scenes: [
    // Lockup: on screen at rest on frame 0, pushed out at t 0, rebuilt at the end, then holds.
    {
      id: 'lockup', world: 0, t0: beat(43), t1: bar(13), in: 'pan',
      wrap: { exit: 0, dy: -1100 },
      breath: { t0: beat(47), t1: beat(51), amount: 0.01 },
      lines: [
        { id: 'OW', text: 'OpenWiki', font: 'display', cap: 184, track: -30, pairs: PAIRS, anchor: 'C', baseline: 496, color: 'fg',
          enter: { at: beat(43.25), from: 120, spring: 'LAND', blur: 16, stagger: 32 }, mis: 'land' },
        { id: 'URL', text: 'github.com/ckryptickunal/OpenWiki', font: 'label', cap: 40, track: 0, pairs: { ry: 18, kr: 6, pe: 6, ki: 6 }, anchor: 'C', baseline: 672, color: 'fg',
          enter: { at: beat(45), from: -72, spring: 'LAND', blur: 10, stagger: 128 }, clipBelow: 592 },
      ],
      rules: [
        { id: 'RULE', x0: 443, x1: 1478, y: 584, h: 6, color: 'accent', draw: { at: beat(44.5), spring: 'LINE', from: 'C' } },
      ],
      crumbs: [
        { id: 'FREE', text: 'FREE AND OPEN SOURCE · MIT', at: beat(46), anchor: 'C', baseline: 784, color: 'muted', cursor: false },
      ],
    },
    // 1. You watched it.  Rises as the lockup leaves, so the loop never shows an empty frame.
    {
      id: 'watched', world: 0, t0: 0, t1: beat(4.5), in: 'none',
      lines: [
        { id: 'WATCHED', text: 'You watched it.', cap: H1, track: -26, pairs: PAIRS, baseline: 560, color: 'fg', enter: enterA(0), exit: out(beat(3.5)) },
      ],
      crumbs: [
        { id: 'YC', text: 'Y COMBINATOR · HOW TO GET AI STARTUP IDEAS · 43:49', at: beat(1), baseline: 688, color: 'muted', cursor: false, exit: out(beat(3.5)) },
      ],
    },
    // 2. You saved it.
    {
      id: 'saved', world: 0, t0: beat(4), t1: beat(8), in: 'none',
      lines: [
        { id: 'SAVED', text: 'You saved it.', cap: H1, track: -26, pairs: PAIRS, baseline: 560, color: 'fg', enter: enterA(beat(4)) },
      ],
      crumbs: [
        { id: 'PG', text: 'PAULGRAHAM.COM · DO THINGS THAT DON’T SCALE', at: beat(5), baseline: 688, color: 'muted', cursor: false },
      ],
    },
    // 3. You can't find it.  Hard cut, the line is on screen the frame the cut lands; the question types itself.
    {
      id: 'find', world: 0, t0: beat(8), t1: beat(14), in: 'cut',
      punch: { at: beat(12), z: 1.05 },
      lines: [
        { id: 'CANT', text: 'You can’t find it.', cap: H1, track: -26, pairs: PAIRS, baseline: 560, color: 'fg',
          enter: { at: beat(8), from: 0, spring: 'LAND', blur: 0, stagger: 0, pop: true } },
      ],
      crumbs: [
        { id: 'Q', text: 'which video had the warm network advice?', at: beat(9), baseline: 688, color: 'accent', blink: [beat(10.5), beat(11.9)] },
      ],
    },
    // 4. Your AI starts over.  Smash-pan to the next world.
    {
      id: 'agent', world: 1, t0: beat(14), t1: beat(20), in: 'pan',
      punch: { at: beat(18), z: 1.05 },
      lines: [
        { id: 'YOURAI', text: 'Your AI', cap: H1, track: -26, pairs: PAIRS, baseline: B1, color: 'fg', enter: enterA(beat(14)) },
        { id: 'OVER', text: 'starts over.', cap: H1, track: -26, pairs: PAIRS, baseline: B2, color: 'accent', enter: enterA(beat(14.5)), mis: 'land' },
      ],
      crumbs: [
        { id: 'RAW', text: 'ONE IDEA MATCHES 68 RAW FILES · 611,954 TOKENS', at: beat(16.5), baseline: C1, color: 'muted', cursor: false },
      ],
    },
    // 5. OpenWiki compiles it once.  Revealed through the letterforms of "starts over."
    {
      id: 'compile', world: 1, t0: beat(20), t1: beat(25), in: 'mask', mask: { line: 'OVER' },
      lines: [
        { id: 'OPENWIKI', text: 'OpenWiki', cap: H1, track: -26, pairs: PAIRS, baseline: B1, color: 'accent', exit: out(beat(24)) },
        { id: 'ONCE', text: 'compiles it once.', cap: H1, track: -26, pairs: PAIRS, baseline: B2, color: 'fg', enter: enterA(beat(21)), exit: out(beat(24)) },
      ],
    },
    // 6. A wiki you own.  The real Founder Book link graph blooms beside it.
    {
      id: 'wiki', world: 1, t0: beat(24.5), t1: beat(31), in: 'none',
      lines: [
        { id: 'AWIKI', text: 'A wiki', cap: H1, track: -26, pairs: PAIRS, baseline: B1, color: 'fg', enter: enterA(beat(24.75)) },
        { id: 'OWN', text: 'you own.', cap: H1, track: -26, pairs: PAIRS, baseline: B2, color: 'accent', enter: enterA(beat(25.25)) },
      ],
      crumbs: [
        { id: 'FB1', text: 'FOUNDER BOOK, SAME PIPELINE:', at: beat(26.5), baseline: C1, color: 'muted', cursor: false },
        { id: 'FB2', text: '1,219 VIDEOS + 354 ESSAYS → 8,768 PAGES', at: beat(27.5), baseline: C2, color: 'fg', cursor: false },
      ],
      draw: drawGraph, active: [[beat(24.75), beat(31) + 0.5]],
    },
    // 7. You find the moment.  Pan again; the answer to the question from beat 3.
    {
      id: 'moment', world: -1, t0: beat(31), t1: beat(37.5), in: 'cut',
      lines: [
        { id: 'YOUFIND', text: 'You find', cap: H1, track: -26, pairs: PAIRS, baseline: B1, color: 'fg', enter: { at: beat(31), from: 0, spring: 'LAND', blur: 0, stagger: 0, pop: true }, exit: out(beat(36.5)) },
        { id: 'MOMENT', text: 'the moment.', cap: H1, track: -26, pairs: PAIRS, baseline: B2, color: 'accent', enter: enterA(beat(31.5)), mis: 'land', exit: out(beat(36.5)) },
      ],
      crumbs: [
        { id: 'CMD', text: '$ openwiki search warm network', at: beat(32.5), baseline: C1, color: 'muted', exit: out(beat(36.5)) },
        { id: 'HIT', text: '→ Why You\'re Getting Zero Replies To Your Cold Emails [3:46]', at: beat(34), baseline: C2, color: 'fg', cursor: false, exit: out(beat(36.5)) },
      ],
    },
    // 8. Your AI reads less.  Hard cut; "Your AI" is back, the payoff lands under it.
    {
      id: 'less', world: -1, t0: beat(36.75), t1: beat(43), in: 'none',
      lines: [
        { id: 'YOURAI2', text: 'Your AI', cap: H1, track: -26, pairs: PAIRS, baseline: B1, color: 'fg', enter: enterA(beat(37)) },
        { id: 'LESS', text: 'reads less.', cap: H1, track: -26, pairs: PAIRS, baseline: B2, color: 'accent', enter: enterA(beat(37.5)), mis: 'land' },
      ],
      crumbs: [
        { id: 'MP', text: 'MEDIAN SUMMARY PAGE: 786 TOKENS', at: beat(39), baseline: C1, color: 'fg', cursor: false },
        { id: 'MS', text: 'MEDIAN RAW SOURCE: 3,397 TOKENS', at: beat(40), baseline: C2, color: 'muted', cursor: false },
      ],
    },
  ],
};
