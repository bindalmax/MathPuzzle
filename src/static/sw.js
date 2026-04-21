const CACHE_NAME = 'mathpuzzle-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/responsive.css',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Lexend:wght@300;400;700&display=swap'
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: Clear old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: Network First for pages, Cache First for static assets
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // For static assets, try cache first
  if (STATIC_ASSETS.includes(url.pathname) || url.origin !== location.origin) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request);
      })
    );
    return;
  }

  // For pages (e.g., /, /game), try network first
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        // If network fails, return cached page or offline message
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          
          // Basic offline fallback for navigation
          if (event.request.mode === 'navigate') {
             return caches.match('/');
          }
        });
      })
  );
});
