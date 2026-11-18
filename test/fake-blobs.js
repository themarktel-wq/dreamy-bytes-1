/* In-memory imitation of a Netlify Blobs store (same calls and ETag rules), for tests and local runs. */
'use strict';
function fakeStore() {
  const m = new Map(); let n = 0;
  const tick = () => new Promise((r) => setTimeout(r, Math.random() * 4)); // let requests interleave
  const etag = () => '"' + (++n) + '"';
  const out = (e, type) => (type === 'json' ? JSON.parse(e.text) : type === 'arrayBuffer' ? e.bin : e.text);
  return {
    m,
    async getWithMetadata(k, o = {}) { await tick(); const e = m.get(k); if (!e) return null; if (o.etag && o.etag === e.etag) return { data: null, etag: e.etag, metadata: e.metadata }; return { data: out(e, o.type), etag: e.etag, metadata: e.metadata }; },
    async getMetadata(k) { await tick(); const e = m.get(k); return e ? { etag: e.etag, metadata: e.metadata } : null; },
    async get(k, o = {}) { await tick(); const e = m.get(k); return e ? out(e, o.type) : null; },
    async setJSON(k, v, o = {}) { await tick(); return this._set(k, { text: JSON.stringify(v) }, o); },
    async set(k, v, o = {}) { await tick(); return this._set(k, { bin: v, text: '' }, o); },
    _set(k, e, o) {
      const cur = m.get(k);
      if (o.onlyIfNew && cur) return { modified: false };
      if (o.onlyIfMatch && (!cur || cur.etag !== o.onlyIfMatch)) return { modified: false };
      const t = etag(); m.set(k, { ...e, etag: t, metadata: o.metadata || {} }); return { modified: true, etag: t };
    },
    async delete(k) { await tick(); m.delete(k); },
  };
}
module.exports = { fakeStore };
