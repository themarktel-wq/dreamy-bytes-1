/* Lahore Mobile service worker: offline app shell + runtime cache. Bump VERSION on every deploy. */
const VERSION = 'lm-v3';
const SHELL = ['./', 'index.html', 'css/style.css', 'core/memstore.js', 'core/core.js', 'core/seed-images.js', 'js/ui.js', 'js/api.js', 'js/router.js', 'js/shop.js', 'js/admin.js', 'js/main.js',
  'manifest.webmanifest', 'icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png'];

self.addEventListener('install', (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Same-origin: network-first so updates show up, cache fallback for offline.
  if (url.origin === location.origin && url.pathname.includes('/api/')) return;
  if (url.origin === location.origin) {
    e.respondWith(fetch(req).then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); return res; })
      .catch(() => caches.match(req).then((r) => r || caches.match('index.html'))));
    return;
  }
  // Fonts: cache-first.
  if (/fonts\.(googleapis|gstatic)\.com/.test(url.host)) {
    e.respondWith(caches.match(req).then((r) => r || fetch(req).then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); return res; })));
  }
});
self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  const url = './' + ((e.notification.data && e.notification.data.url) || '');
  e.waitUntil(self.clients.matchAll({ type: 'window' }).then((cs) => (cs[0] ? cs[0].focus().then((c) => c.navigate(url)) : self.clients.openWindow(url))));
});
