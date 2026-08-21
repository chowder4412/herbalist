const CACHE_NAME = 'herbalist-pwa-v4.4';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((key) => caches.delete(key)));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Never intercept POST/PUT/DELETE or /api/ endpoints — let native browser fetch handle them directly
  if (event.request.method !== 'GET' || event.request.url.includes('/api/')) {
    return;
  }

  event.respondWith(
    fetch(event.request).catch(async () => {
      const cached = await caches.match(event.request);
      if (cached) return cached;
      return new Response('<!-- Herbalist AI Offline Mode -->', {
        headers: { 'Content-Type': 'text/html' }
      });
    })
  );
});
