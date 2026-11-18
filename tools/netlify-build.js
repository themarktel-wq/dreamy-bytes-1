/* Netlify build step: copies the public app into dist/ and stamps the build id.
   The stamp changes sw.js on every deploy that changes the app, so installed apps update themselves. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'dist');
const PUBLIC = ['index.html', 'manifest.webmanifest', 'sw.js', 'css', 'js', 'core', 'assets', 'icons'];

fs.rmSync(OUT, { recursive: true, force: true });
const h = crypto.createHash('sha1');
const copy = (rel) => {
  const src = path.join(ROOT, rel), dst = path.join(OUT, rel), st = fs.statSync(src);
  if (st.isDirectory()) { fs.mkdirSync(dst, { recursive: true }); for (const n of fs.readdirSync(src).sort()) copy(path.join(rel, n)); return; }
  const buf = fs.readFileSync(src); h.update(rel); h.update(buf);
  fs.mkdirSync(path.dirname(dst), { recursive: true }); fs.writeFileSync(dst, buf);
};
PUBLIC.forEach(copy);
const build = h.digest('hex').slice(0, 12);
const sw = path.join(OUT, 'sw.js');
fs.writeFileSync(sw, fs.readFileSync(sw, 'utf8').replace(/const VERSION = '[^']*';/, `const VERSION = 'lm-${build}';`));
fs.writeFileSync(path.join(ROOT, 'netlify/functions/build.json'), JSON.stringify({ build }) + '\n');
console.log(`Built dist/ (version lm-${build})`);
