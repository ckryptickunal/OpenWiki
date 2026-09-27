// Assemble src/film.html from the skill's engine template, our FILM block and the graph data.
// Run: node src/assemble.mjs  (then the skill's build.mjs embeds the fonts)
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
const here = path.dirname(new URL(import.meta.url).pathname);
const tpl = fs.readFileSync(path.join(os.homedir(), '.claude/skills/motion-launch-videos/templates/film.html'), 'utf8');
const block = fs.readFileSync(path.join(here, 'film-block.js'), 'utf8');
const graph = fs.readFileSync(path.join(here, 'graph.json'), 'utf8');
const a = tpl.indexOf('const BPM = 120;'), b = tpl.indexOf('/* ==========================================================================\n * ENGINE');
if (a < 0 || b < 0) throw new Error('template markers not found');
let html = tpl.slice(0, a) + block + '\n' + tpl.slice(b);
html = html.replace(/@font-face\{[^\n]*\n/g, '');
const faces = [
  '@font-face{font-family:"Inter Display";font-style:normal;font-weight:700;font-display:block;src:url(data:font/woff2;base64,__FONT:inter-display-latin-700-normal.woff2__) format("woff2")}',
  '@font-face{font-family:"Inter Display";font-style:normal;font-weight:600;font-display:block;src:url(data:font/woff2;base64,__FONT:inter-display-latin-600-normal.woff2__) format("woff2")}',
  '@font-face{font-family:"JetBrains Mono";font-style:normal;font-weight:500;font-display:block;src:url(data:font/woff2;base64,__FONT:jetbrains-mono-latin-500-normal.woff2__) format("woff2")}',
].join('\n') + '\n';
html = html.replace('<style>\n', '<style>\n' + faces);
html = html.replace('<canvas id="c"', `<script>window.GRAPH=${graph};</script>\n<canvas id="c"`);
fs.writeFileSync(path.join(here, 'film.html'), html);
console.log('assembled', html.length);
