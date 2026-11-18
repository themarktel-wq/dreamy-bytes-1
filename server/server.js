/* Lahore Mobile Wholesale — server.
   Zero dependencies: Node 22+ (node:http, node:sqlite, node:crypto).
   Run:  node --no-warnings server/server.js
   Env:  PORT=8080  DATA_DIR=./data  ADMIN_PHONE=03000000000  ADMIN_PASSWORD=...  DEMO=1 (adds sample shops and orders) */
'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { DatabaseSync } = require('node:sqlite');
const { createCore } = require('../core/core.js');
const { createMemStore } = require('../core/memstore.js');
const { SEED_IMAGES } = require('../core/seed-images.js');
const webpush = require('./webpush.js');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PORT) || 8080;
const DATA = path.resolve(process.env.DATA_DIR || path.join(ROOT, 'data'));
const UPLOADS = path.join(DATA, 'uploads');
const SECURE = process.env.COOKIE_SECURE === '1';
fs.mkdirSync(UPLOADS, { recursive: true });

/* ---------- storage: SQLite document table, cached in memory ---------- */
const db = new DatabaseSync(path.join(DATA, 'lahore-mobile.db'));
db.exec('PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL; CREATE TABLE IF NOT EXISTS docs (col TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY (col, id));');
const initial = {};
for (const row of db.prepare('SELECT col, data FROM docs').all()) (initial[row.col] ||= []).push(JSON.parse(row.data));
const upsert = db.prepare('INSERT INTO docs (col, id, data) VALUES (?, ?, ?) ON CONFLICT (col, id) DO UPDATE SET data = excluded.data');
const remove = db.prepare('DELETE FROM docs WHERE col = ? AND id = ?');
const store = createMemStore(initial, {
  onCommit(changed) {
    db.exec('BEGIN');
    try {
      for (const { c, id, doc } of changed) doc === undefined ? remove.run(c, id) : upsert.run(c, id, JSON.stringify(doc));
      db.exec('COMMIT');
    } catch (e) { db.exec('ROLLBACK'); console.error('DB write failed', e); throw e; }
  },
});

/* ---------- crypto & files ---------- */
const deps = {
  hashPassword(pw) { const salt = crypto.randomBytes(16).toString('hex'); return `scrypt$${salt}$${crypto.scryptSync(pw, salt, 32).toString('hex')}`; },
  verifyPassword(pw, stored) {
    const [kind, salt, hash] = String(stored || '').split('$');
    if (kind !== 'scrypt' || !salt || !hash) return false;
    const a = crypto.scryptSync(pw, salt, 32), b = Buffer.from(hash, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  },
  sha: (s) => crypto.createHash('sha256').update(String(s)).digest('hex'),
  rid: (n) => crypto.randomBytes(n).toString('hex'),
  now: () => Date.now(),
  saveImage(dataUrl) {
    const m = /^data:image\/(jpeg|png|webp);base64,(.+)$/.exec(dataUrl);
    if (!m) throw Object.assign(new Error('bad image'), { status: 400 });
    const name = crypto.randomBytes(10).toString('hex') + '.' + (m[1] === 'jpeg' ? 'jpg' : m[1]);
    fs.writeFileSync(path.join(UPLOADS, name), Buffer.from(m[2], 'base64'));
    return '/uploads/' + name;
  },
};
const core = createCore({ store, deps });
const adminPassword = process.env.ADMIN_PASSWORD || (process.env.DEMO === '1' ? 'admin123' : crypto.randomBytes(6).toString('base64url'));
if (core.seed({ demo: process.env.DEMO === '1', adminPhone: process.env.ADMIN_PHONE || '03000000000', adminPassword, images: SEED_IMAGES })) {
  console.log(`\n  First run: created the owner account\n  Mobile:   ${process.env.ADMIN_PHONE || '03000000000'}\n  Password: ${adminPassword}\n  Sign in and change the password from Admin → Settings.\n`);
}

/* ---------- automatic daily backups: DATA_DIR/backups, last 14 days kept ---------- */
const BACKUPS = path.join(DATA, 'backups');
function autoBackup() {
  try {
    fs.mkdirSync(BACKUPS, { recursive: true });
    const name = `lahore-mobile-${new Date().toISOString().slice(0, 10)}.db`, file = path.join(BACKUPS, name);
    if (!fs.existsSync(file)) { db.exec(`VACUUM INTO '${file.replace(/'/g, "''")}'`); console.log('Backup saved', name); }
    const old = fs.readdirSync(BACKUPS).filter((n) => n.endsWith('.db')).sort().slice(0, -14);
    for (const n of old) fs.unlinkSync(path.join(BACKUPS, n));
  } catch (e) { console.error('Backup failed', e.message); }
}
autoBackup(); setInterval(autoBackup, 3600e3).unref();

/* ---------- push notifications ---------- */
const VAPID = webpush.loadVapid(path.join(DATA, 'vapid.json'));
const VAPID_SUBJECT = process.env.VAPID_SUBJECT || 'mailto:admin@example.com';
function pushOut(ev) {
  if (!ev.title) return;
  for (const sub of core.pushTargets(ev.to)) {
    webpush.send(sub, { title: ev.title, body: ev.body || '', url: ev.url || '#/' }, VAPID, VAPID_SUBJECT).then((r) => { if (r.gone) core.dropPushSub(sub.id); else if (!r.ok && process.env.PUSH_DEBUG) console.warn('push failed', r); });
  }
}

/* ---------- live updates (Server-Sent Events) ---------- */
const clients = new Set();
function userFromToken(token) {
  const r = core.handle({ method: 'GET', path: '/api/me', token });
  return r.body && r.body.user;
}
function broadcast(events) {
  for (const ev of events || []) {
    for (const c of clients) {
      const hit = (ev.to === 'all' && c.role === 'shop') || (ev.to === 'admin' && (c.role === 'admin' || c.role === 'staff')) || ev.to.endsWith(':' + c.userId);
      if (hit) c.res.write(`event: change\ndata: ${JSON.stringify({ type: ev.type, title: ev.title || '', url: ev.url || '' })}\n\n`);
    }
    pushOut(ev);
  }
}
setInterval(() => { for (const c of clients) c.res.write(': ping\n\n'); }, 25000).unref();

/* ---------- app build id: changes whenever any app file changes, so installed apps update themselves ---------- */
let BUILD = '', buildAt = 0;
function appBuild() {
  if (Date.now() - buildAt < 15000 && BUILD) return BUILD;
  const h = crypto.createHash('sha1');
  const walk = (rel) => {
    const abs = path.join(ROOT, rel); let st; try { st = fs.statSync(abs); } catch { return; }
    if (st.isDirectory()) { for (const n of fs.readdirSync(abs).sort()) walk(path.join(rel, n)); return; }
    h.update(rel + ':' + st.size + ':' + st.mtimeMs + ';');
  };
  ['index.html', 'manifest.webmanifest', 'sw.js', 'css', 'js', 'core', 'icons'].forEach(walk);
  BUILD = h.digest('hex').slice(0, 12); buildAt = Date.now();
  return BUILD;
}

/* ---------- HTTP ---------- */
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon' };
const PUBLIC = ['index.html', 'manifest.webmanifest', 'sw.js', 'css/', 'js/', 'core/', 'assets/', 'icons/'];
const hits = new Map();
function rateLimited(ip) {
  const t = Date.now(), h = hits.get(ip) || { n: 0, at: t };
  if (t - h.at > 60e3) { h.n = 0; h.at = t; }
  h.n++; hits.set(ip, h);
  return h.n > 600;
}
setInterval(() => { const t = Date.now(); for (const [k, v] of hits) if (t - v.at > 120e3) hits.delete(k); }, 60e3).unref();

function cookies(req) { return Object.fromEntries((req.headers.cookie || '').split(';').map((c) => c.trim().split('=')).filter((p) => p[0]).map(([k, ...v]) => [k, decodeURIComponent(v.join('='))])); }
function tokenOf(req) { const a = req.headers.authorization || ''; return a.startsWith('Bearer ') ? a.slice(7) : cookies(req).lm_s || ''; }
function send(res, status, body, headers = {}) {
  const data = typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers });
  res.end(data);
}
function readBody(req, limit = 4e6) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', (c) => { size += c.length; if (size > limit) { reject(Object.assign(new Error('too large'), { status: 413 })); req.destroy(); } else chunks.push(c); });
    req.on('end', () => { try { resolve(chunks.length ? JSON.parse(Buffer.concat(chunks).toString('utf8')) : {}); } catch { reject(Object.assign(new Error('bad json'), { status: 400 })); } });
    req.on('error', reject);
  });
}
function serveFile(req, res, file, cache, transform) {
  fs.readFile(file, (err, buf) => {
    if (err) return send(res, 404, 'Not found', { 'Content-Type': 'text/plain' });
    if (transform) buf = Buffer.from(transform(buf.toString('utf8')));
    const etag = '"' + crypto.createHash('sha1').update(buf).digest('base64url').slice(0, 20) + '"';
    const head = { 'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Cache-Control': cache, ETag: etag, 'X-Content-Type-Options': 'nosniff' };
    if (req.headers['if-none-match'] === etag) { res.writeHead(304, head); return res.end(); }
    res.writeHead(200, head);
    res.end(req.method === 'HEAD' ? undefined : buf);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const ip = req.socket.remoteAddress || '';
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'same-origin');
  try {
    if (url.pathname === '/api/events') {
      const u = userFromToken(tokenOf(req));
      if (!u) return send(res, 401, { error: 'Please sign in' });
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store', Connection: 'keep-alive', 'X-Accel-Buffering': 'no' });
      res.write('retry: 5000\n\n');
      const c = { res, role: u.role, userId: u.id }; clients.add(c);
      req.on('close', () => clients.delete(c));
      return;
    }
    if (url.pathname === '/api/push/key') return send(res, 200, { key: VAPID.publicKeyB64 });
    if (url.pathname === '/api/version') return send(res, 200, { build: appBuild() }, { 'X-App-Build': appBuild() });
    if (url.pathname.startsWith('/api/')) {
      if (rateLimited(ip)) return send(res, 429, { error: 'Too many requests. Please wait a minute.' });
      if (req.method !== 'GET' && req.headers['content-type'] && !req.headers['content-type'].includes('application/json')) return send(res, 415, { error: 'Send JSON' });
      const body = ['POST', 'PUT', 'PATCH'].includes(req.method) ? await readBody(req) : {};
      const r = core.handle({ method: req.method, path: url.pathname, query: Object.fromEntries(url.searchParams), body, token: tokenOf(req) });
      if (r.crash) console.error(new Date().toISOString(), req.method, url.pathname, r.crash);
      const headers = { 'X-App-Build': appBuild() };
      if (r.token) headers['Set-Cookie'] = `lm_s=${r.token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 86400}${SECURE ? '; Secure' : ''}`;
      if (r.clearToken) headers['Set-Cookie'] = `lm_s=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${SECURE ? '; Secure' : ''}`;
      send(res, r.status, r.body, headers);
      broadcast(r.events);
      return;
    }
    if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, { error: 'Method not allowed' });
    if (url.pathname.startsWith('/uploads/')) {
      const name = path.basename(url.pathname);
      return serveFile(req, res, path.join(UPLOADS, name), 'public, max-age=31536000, immutable');
    }
    let rel = decodeURIComponent(url.pathname).replace(/^\/+/, '') || 'index.html';
    if (rel.includes('..') || !PUBLIC.some((p) => rel === p || (p.endsWith('/') && rel.startsWith(p)))) rel = 'index.html';
    // App code is always revalidated (cheap 304s), so a new version reaches every phone on its next open.
    const code = /\.(html|js|css|webmanifest|json)$/.test(rel);
    serveFile(req, res, path.join(ROOT, rel), code ? 'no-cache' : 'public, max-age=86400',
      rel === 'sw.js' ? (t) => t.replace(/const VERSION = '[^']*';/, `const VERSION = 'lm-${appBuild()}';`) : null);
  } catch (e) {
    if (!res.headersSent) send(res, e.status || 500, { error: e.status === 413 ? 'Upload is too large' : e.status === 400 ? 'Invalid request' : 'Server error' });
    if (!e.status) console.error(e);
  }
});
server.listen(PORT, () => console.log(`Lahore Mobile running on http://localhost:${PORT}  (data: ${DATA})`));
