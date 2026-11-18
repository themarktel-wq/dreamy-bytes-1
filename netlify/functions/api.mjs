/* Lahore Mobile — the whole backend as one Netlify Function, with data in Netlify Blobs.
   Same business rules as server/server.js (core/core.js); only storage and live updates differ:
   - each collection (products, orders, …) is one JSON blob in the "lm-data" store
   - writes take a short lock and check that nothing changed since the data was read, else the request is re-run
   - photos go to the "lm-uploads" store and are served from /uploads/…
   - live updates: the app polls /api/poll (functions cannot hold an open connection)
   Env (Site settings → Environment variables): ADMIN_PHONE, ADMIN_PASSWORD (first sign-in), optional VAPID_SUBJECT. */
import crypto from 'node:crypto';
// Static imports so Netlify's bundler packs these files into the function.
import coreMod from '../../core/core.js';
import memMod from '../../core/memstore.js';
import seedMod from '../../core/seed-images.js';
import webpush from '../../server/webpush.js';
import buildInfo from './build.json' with { type: 'json' };

const { createCore } = coreMod, { createMemStore } = memMod, { SEED_IMAGES } = seedMod;
const BUILD = buildInfo.build;

export const config = { path: ['/api/*', '/uploads/*'] };

const COLS = ['settings', 'users', 'sessions', 'products', 'orders', 'stockMoves', 'purchases', 'messages', 'announcements', 'requests', 'claims', 'counters', 'deals', 'suppliers', 'supplierLedger', 'pushSubs'];
const EVENTS = '_events', LOCK = '_lock';

/* ---------- stores (tests inject fakes) ---------- */
let stores = null;
export function _setStores(s) { stores = s; cache.clear(); }
async function getStores() {
  if (stores) return stores;
  const { getStore } = await import('@netlify/blobs');
  stores = { data: getStore({ name: 'lm-data', consistency: 'strong' }), uploads: getStore({ name: 'lm-uploads', consistency: 'strong' }) };
  return stores;
}

/* ---------- data loading with a warm-instance cache (ETags avoid re-downloading unchanged collections) ---------- */
const cache = new Map(); // col -> { etag, text }
async function loadAll(data) {
  await Promise.all([...COLS, EVENTS].map(async (c) => {
    const had = cache.get(c);
    const r = await data.getWithMetadata(c, had ? { etag: had.etag } : {});
    if (!r) { cache.delete(c); return; }
    if (had && r.etag === had.etag) return;
    cache.set(c, { etag: r.etag, text: typeof r.data === 'string' ? r.data : JSON.stringify(r.data) });
  }));
  const initial = {};
  for (const c of COLS) { const e = cache.get(c); if (e) initial[c] = JSON.parse(e.text); }
  return initial;
}

async function withLock(data, fn) {
  const me = crypto.randomBytes(8).toString('hex'), until = Date.now() + 9000;
  for (;;) {
    const r = await data.setJSON(LOCK, { me, at: Date.now() }, { onlyIfNew: true });
    if (r.modified) break;
    const cur = await data.getWithMetadata(LOCK, { type: 'json' });
    if (cur && cur.data && Date.now() - cur.data.at > 15000) { const s = await data.setJSON(LOCK, { me, at: Date.now() }, { onlyIfMatch: cur.etag }); if (s.modified) break; }
    if (Date.now() > until) throw Object.assign(new Error('The shop is busy. Please try again.'), { status: 503 });
    await new Promise((res) => setTimeout(res, 80 + Math.random() * 160));
  }
  try { return await fn(); } finally { await data.delete(LOCK).catch(() => {}); }
}

/* ---------- crypto deps (same as the Node server) ---------- */
function makeDeps(pendingUploads) {
  return {
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
      pendingUploads.push({ name, type: 'image/' + m[1], buf: Buffer.from(m[2], 'base64') });
      return '/uploads/' + name;
    },
  };
}

/* ---------- one attempt: load, run the business rules, save if anything changed ---------- */
async function attempt(data, uploads, req) {
  const initial = await loadAll(data);
  const etags = Object.fromEntries([...COLS, EVENTS].map((c) => [c, cache.get(c)?.etag || null]));
  const changedCols = new Set(), pendingUploads = [];
  const store = createMemStore(initial, { onCommit(changed) { changed.forEach((x) => changedCols.add(x.c)); } });
  const core = createCore({ store, deps: makeDeps(pendingUploads) });

  if (!store.get('settings', 'main')) {
    const phone = process.env.ADMIN_PHONE, pw = process.env.ADMIN_PASSWORD;
    if (!phone || !pw || pw.length < 6) return { status: 503, body: { error: 'Setup needed: add ADMIN_PHONE and ADMIN_PASSWORD (6+ characters) in Netlify → Site configuration → Environment variables, then redeploy.' } };
    core.seed({ demo: process.env.DEMO === '1', adminPhone: phone, adminPassword: pw, images: SEED_IMAGES });
  }
  if (process.env.OWNER_RESET_PASSWORD) core.ownerReset(process.env.OWNER_RESET_PASSWORD);

  let out;
  if (req.special === 'poll') {
    const me = core.handle({ method: 'GET', path: '/api/me', token: req.token }).body;
    const u = me && me.user; if (!u) return { status: 401, body: { error: 'Please sign in' } };
    const evs = (cache.get(EVENTS) ? JSON.parse(cache.get(EVENTS).text) : []).filter((e) => e.at > Number(req.query.since || 0) && hit(e, u));
    return { status: 200, body: { now: Date.now(), events: evs.map(({ type, title, url }) => ({ type, title: title || '', url: url || '' })) } };
  }
  if (req.special === 'pushKey') {
    // VAPID key pair lives in the data store so push subscriptions stay valid across deploys.
    return { status: 200, body: { key: (await vapid(data)).publicKeyB64 } };
  }
  out = core.handle(req);
  if (!changedCols.size && !pendingUploads.length) return out;

  await withLock(data, async () => {
    // Re-check: if another request changed any collection since we read it, start again with fresh data.
    const now = await Promise.all([...COLS, EVENTS].map(async (c) => [c, (await data.getMetadata(c))?.etag || null]));
    if (now.some(([c, e]) => e !== etags[c])) throw RETRY;
    for (const f of pendingUploads) await uploads.set(f.name, f.buf.buffer.slice(f.buf.byteOffset, f.buf.byteOffset + f.buf.byteLength), { metadata: { type: f.type } });
    const dump = store.dump();
    for (const c of changedCols) {
      const r = await data.setJSON(c, dump[c] || []);
      cache.set(c, { etag: r.etag, text: JSON.stringify(dump[c] || []) });
    }
    if (out.events && out.events.length) {
      const prev = cache.get(EVENTS) ? JSON.parse(cache.get(EVENTS).text) : [];
      const at = Date.now(), next = prev.concat(out.events.map((e) => ({ ...e, at }))).filter((e) => at - e.at < 3 * 864e5).slice(-200);
      const r = await data.setJSON(EVENTS, next); cache.set(EVENTS, { etag: r.etag, text: JSON.stringify(next) });
    }
  });
  out.pushes = (out.events || []).filter((e) => e.title).map((e) => ({ e, subs: core.pushTargets(e.to) }));
  return out;
}
const RETRY = new Error('retry');
const hit = (ev, u) => (ev.to === 'all' && u.role === 'shop') || (ev.to === 'admin' && (u.role === 'admin' || u.role === 'staff')) || String(ev.to).endsWith(':' + u.id);

let VAPID = null;
async function vapid(data) {
  if (VAPID) return VAPID;
  let jwk = await data.get('_vapid', { type: 'json' });
  if (!jwk) { jwk = webpush.newVapidJwk(); const r = await data.setJSON('_vapid', jwk, { onlyIfNew: true }); if (!r.modified) jwk = await data.get('_vapid', { type: 'json' }); }
  return (VAPID = webpush.vapidFromJwk(jwk));
}

/* ---------- HTTP ---------- */
const json = (status, body, headers = {}) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-App-Build': BUILD, ...headers } });
function tokenOf(request) {
  const a = request.headers.get('authorization') || ''; if (a.startsWith('Bearer ')) return a.slice(7);
  const m = /(?:^|;\s*)lm_s=([^;]+)/.exec(request.headers.get('cookie') || ''); return m ? decodeURIComponent(m[1]) : '';
}

export default async function handler(request, context) {
  const url = new URL(request.url);
  try {
    const { data, uploads } = await getStores();
    if (url.pathname.startsWith('/uploads/')) {
      const name = url.pathname.slice(9).replace(/[^\w.-]/g, '');
      const r = await uploads.getWithMetadata(name, { type: 'arrayBuffer' });
      if (!r) return new Response('Not found', { status: 404 });
      return new Response(r.data, { headers: { 'Content-Type': (r.metadata && r.metadata.type) || 'image/jpeg', 'Cache-Control': 'public, max-age=31536000, immutable' } });
    }
    if (url.pathname === '/api/version') return json(200, { build: BUILD });
    if (url.pathname === '/api/events') return json(404, { error: 'Live connection is not used on this host' });

    let body = {};
    if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
      const text = await request.text();
      if (text.length > 4e6) return json(413, { error: 'Upload is too large' });
      try { body = text ? JSON.parse(text) : {}; } catch { return json(400, { error: 'Invalid request' }); }
    }
    const secure = url.protocol === 'https:';
    const req = { method: request.method, path: url.pathname, query: Object.fromEntries(url.searchParams), body, token: tokenOf(request),
      special: url.pathname === '/api/poll' ? 'poll' : url.pathname === '/api/push/key' ? 'pushKey' : null };

    let out;
    for (let i = 0; ; i++) {
      try { out = await attempt(data, uploads, req); break; }
      catch (e) { if (e !== RETRY || i >= 4) throw e; }
    }
    if (out.crash) console.error(request.method, url.pathname, out.crash);
    if (out.body && out.status === 200 && url.pathname === '/api/info') out.body = { ...out.body, live: 'poll' };

    if (out.pushes && out.pushes.length) {
      const v = await vapid(data), subject = process.env.VAPID_SUBJECT || 'mailto:admin@example.com';
      const sends = out.pushes.flatMap(({ e, subs }) => subs.map((sub) => webpush.send(sub, { title: e.title, body: e.body || '', url: e.url || '#/' }, v, subject).catch(() => null)));
      const all = Promise.allSettled(sends);
      if (context && typeof context.waitUntil === 'function') context.waitUntil(all); else await Promise.race([all, new Promise((r) => setTimeout(r, 4000))]);
    }
    const headers = {};
    if (out.token) headers['Set-Cookie'] = `lm_s=${out.token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 86400}${secure ? '; Secure' : ''}`;
    if (out.clearToken) headers['Set-Cookie'] = `lm_s=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure ? '; Secure' : ''}`;
    return json(out.status, out.body, headers);
  } catch (e) {
    console.error(e);
    return json(e.status || 500, { error: e.status ? e.message : 'Server error. Please try again.' });
  }
}
