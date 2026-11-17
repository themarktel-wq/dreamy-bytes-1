/* In-memory document store with transactional rollback.
   Used by the in-browser demo (persisted to localStorage) and as the cache layer of the server store. */
(function (root) {
  'use strict';
  function createMemStore(initial = {}, { onCommit } = {}) {
    const cols = {};
    for (const [c, docs] of Object.entries(initial)) cols[c] = new Map(docs.map((d) => [d.id, d]));
    let journal = null; // [{col, id, before}] while a transaction is open
    const col = (c) => cols[c] || (cols[c] = new Map());
    const clone = (d) => (d === undefined ? undefined : JSON.parse(JSON.stringify(d)));
    function remember(c, id) {
      if (journal && !journal.seen.has(c + '\u0000' + id)) { journal.seen.add(c + '\u0000' + id); journal.list.push({ c, id, before: clone(col(c).get(id)) }); }
    }
    const store = {
      all: (c) => [...col(c).values()],
      get: (c, id) => col(c).get(id),
      put(c, doc) { if (!doc || !doc.id) throw new Error('doc needs an id'); remember(c, doc.id); col(c).set(doc.id, doc); },
      del(c, id) { remember(c, id); col(c).delete(id); },
      tx(fn, { light = false } = {}) {
        if (journal) return fn(); // nested: join the outer transaction
        journal = { list: [], seen: new Set() };
        // Route code mutates docs it got from get()/all() in place, so for write requests keep a copy
        // of every pre-existing doc it reads. Read requests (light) skip this and only journal puts.
        const touched = new Map();
        const origGet = store.get, origAll = store.all;
        const snap = (c, d) => { const k = c + '\u0000' + d.id; if (!touched.has(k) && !journal.seen.has(k)) touched.set(k, { c, id: d.id, before: clone(d) }); };
        if (!light) {
          store.get = (c, id) => { const d = origGet(c, id); if (d) snap(c, d); return d; };
          store.all = (c) => { const ds = origAll(c); ds.forEach((d) => snap(c, d)); return ds; };
        }
        try {
          const r = fn();
          const changed = journal.list.map(({ c, id }) => ({ c, id, doc: col(c).get(id) }));
          journal = null;
          if (onCommit && changed.length) onCommit(changed);
          return r;
        } catch (e) {
          for (const { c, id, before } of journal.list.reverse()) { if (before === undefined) col(c).delete(id); else col(c).set(id, before); }
          for (const { c, id, before } of touched.values()) col(c).set(id, before);
          journal = null;
          throw e;
        } finally { store.get = origGet; store.all = origAll; }
      },
      dump() { const out = {}; for (const [c, m] of Object.entries(cols)) out[c] = [...m.values()]; return out; },
    };
    return store;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { createMemStore }; else root.LMMemStore = { createMemStore };
})(typeof self !== 'undefined' ? self : this);
