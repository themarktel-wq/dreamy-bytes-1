/* Lahore Mobile — API client.
   'server' mode: talks to server/server.js over HTTP (cookies) with live updates over SSE.
   'demo' mode:   runs the same business core (core/core.js) inside the browser, saved to localStorage.
                  Used when no server is reachable (static hosting, artifact preview). */
const API = {
  mode: 'server',
  me: null,          // { user, balance, unread, ... }
  info: null,        // { business, categories, grades, tiers, markets }
  listeners: new Set(),
  es: null,

  async init() {
    if (!window.LM_DEMO) {
      try {
        const r = await fetch('api/info', { credentials: 'same-origin' });
        const isJson = (r.headers.get('content-type') || '').includes('json');
        if (r.ok && isJson) { this.mode = 'server'; this.info = await r.json(); }
        else if (isJson && r.status >= 500) {
          /* A real server answered but is not ready (for example the owner login is not set up yet).
             Never fall back to the sample-data demo here: tell the owner what to fix. */
          const d = await r.json().catch(() => ({}));
          throw Object.assign(new Error(d.error || 'The store is not ready yet.'), { setup: true });
        }
        else this.mode = 'demo';
      } catch (e) { if (e && e.setup) throw e; this.mode = 'demo'; }
    } else this.mode = 'demo';
    if (this.mode === 'demo') { Demo.start(); this.info = await this.get('/api/info'); }
    await this.refreshMe();
  },

  async call(method, path, body) {
    if (this.mode === 'demo') return Demo.call(method, path, body);
    let r;
    try {
      r = await fetch(path.replace(/^\//, ''), { method, credentials: 'same-origin', headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
    } catch { throw Object.assign(new Error('No internet connection. Check your connection and try again.'), { status: 0 }); }
    const build = r.headers.get('X-App-Build');
    if (build) { if (!this.build) this.build = build; else if (build !== this.build) { this.build = build; this.emit({ type: 'newBuild' }); } }
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      if (r.status === 401 && this.me && this.me.user) { this.me = { user: null }; this.emit({ type: 'auth' }); }
      throw Object.assign(new Error(data.error || 'Something went wrong'), { status: r.status });
    }
    return data;
  },
  get(p) { return this.call('GET', p); },
  post(p, b = {}) { return this.call('POST', p, b); },
  put(p, b = {}) { return this.call('PUT', p, b); },
  del(p) { return this.call('DELETE', p); },

  async refreshMe() {
    this.me = await this.get('/api/me').catch(() => ({ user: null }));
    this.connectLive();
    return this.me;
  },
  get user() { return this.me && this.me.user; },
  get isAdmin() { return !!(this.user && (this.user.role === 'admin' || this.user.role === 'staff')); },
  get isOwner() { return !!(this.user && this.user.role === 'admin'); },
  get isShop() { return !!(this.user && this.user.role === 'shop'); },
  get isActiveShop() { return this.isShop && this.user.status === 'active'; },

  async login(phone, password) { const r = await this.post('/api/auth/login', { phone, password }); if (r.token && this.mode === 'demo') Demo.setToken(r.token); await this.refreshMe(); this.emit({ type: 'auth' }); return r; },
  async register(data) { const r = await this.post('/api/auth/register', data); if (r.token && this.mode === 'demo') Demo.setToken(r.token); await this.refreshMe(); this.emit({ type: 'auth' }); return r; },
  async logout() { await this.post('/api/auth/logout').catch(() => {}); if (this.mode === 'demo') Demo.setToken(''); this.me = { user: null }; this.connectLive(); this.emit({ type: 'auth' }); },

  on(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); },
  emit(ev) { this.listeners.forEach((fn) => { try { fn(ev); } catch (e) { console.error(e); } }); },
  connectLive() {
    if (this.mode !== 'server') return;
    if (this.es) { this.es.close(); this.es = null; }
    clearInterval(this.pollTimer); this.pollTimer = null;
    if (!this.user) return;
    if (this.info && this.info.live === 'poll') {
      // Hosts without long-lived connections (Netlify): ask for new events every 30 s while the app is open.
      if (!this.pollSince) this.pollSince = Date.now();
      const tick = async () => {
        if (document.visibilityState !== 'visible' || !this.user) return;
        try { const r = await this.get('/api/poll?since=' + this.pollSince); this.pollSince = r.now; r.events.forEach((e) => this.emit(e)); } catch {}
      };
      this.pollTimer = setInterval(tick, 30000);
      if (!this.pollVis) { this.pollVis = true; document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && this.pollTimer) tick(); }); }
      return;
    }
    if (!('EventSource' in window)) return;
    this.es = new EventSource('api/events');
    this.es.addEventListener('change', (e) => { try { this.emit(JSON.parse(e.data)); } catch {} });
  },
};

/* ---------- In-browser demo backend ---------- */
const Demo = {
  core: null, store: null, token: '',
  KEY: 'lm_wholesale_demo_v4',
  start() {
    let initial = {};
    try { initial = JSON.parse(localStorage.getItem(this.KEY) || '{}'); } catch {}
    try { this.token = localStorage.getItem(this.KEY + '_tok') || ''; } catch {}
    let saveTimer;
    this.store = LMMemStore.createMemStore(initial, { onCommit: () => { clearTimeout(saveTimer); saveTimer = setTimeout(() => this.save(), 150); } });
    const rnd = (n) => [...crypto.getRandomValues(new Uint8Array(n))].map((b) => b.toString(16).padStart(2, '0')).join('');
    this.core = LMCore.createCore({
      store: this.store,
      deps: {
        hashPassword: (p) => 'demo$' + p, verifyPassword: (p, h) => h === 'demo$' + p, sha: (s) => 'k' + s, rid: rnd, now: () => Date.now(),
        saveImage: (dataUrl) => dataUrl,
      },
    });
    if (this.core.seed({ demo: true, images: window.LMSeedImages || {} })) this.save();
  },
  save() { try { localStorage.setItem(this.KEY, JSON.stringify(this.store.dump())); } catch { toast('Browser storage is full. The demo will reset when you reload.', 'info'); } },
  setToken(t) { this.token = t; try { t ? localStorage.setItem(this.KEY + '_tok', t) : localStorage.removeItem(this.KEY + '_tok'); } catch {} },
  reset() { try { localStorage.removeItem(this.KEY); localStorage.removeItem(this.KEY + '_tok'); } catch {} this.token = ''; this.start(); },
  async call(method, path, body) {
    const [p, qs] = path.split('?');
    const r = this.core.handle({ method, path: p, query: Object.fromEntries(new URLSearchParams(qs || '')), body: body ? JSON.parse(JSON.stringify(body)) : {}, token: this.token });
    if (r.crash) console.error(r.crash);
    if (r.clearToken) this.setToken('');
    if (r.status >= 400) throw Object.assign(new Error(r.body.error), { status: r.status });
    if (r.events && r.events.length) setTimeout(() => r.events.forEach((e) => API.emit({ type: e.type })), 0);
    return r.token ? { ...r.body, token: r.token } : r.body;
  },
};
