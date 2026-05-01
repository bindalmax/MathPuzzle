const CACHE_NAME = 'mathpuzzle-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/responsive.css',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

const EXTERNAL_ASSETS = [
  'https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Lexend:wght@300;400;700&display=swap',
  'https://cdn.socket.io/4.7.2/socket.io.min.js'
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([...STATIC_ASSETS, ...EXTERNAL_ASSETS]);
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

// Fetch Strategy
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. Skip non-GET requests and external API calls (like QR code generator)
  // These should not be handled by the service worker to avoid CORS issues
  if (event.request.method !== 'GET' || url.hostname.includes('qrserver.com')) {
    return;
  }

  // 2. Static Assets (Local or Fonts) - Cache First
  if (STATIC_ASSETS.includes(url.pathname) || EXTERNAL_ASSETS.includes(event.request.url)) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request).catch(() => {
          // If fetch fails and no cache, just return nothing (avoid throw)
          return null;
        });
      })
    );
    return;
  }

  // 3. Application Pages - Network First (with offline fallback)
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          
          // Fallback for navigation requests
          if (event.request.mode === 'navigate') {
             return caches.match('/');
          }
          return null;
        });
      })
  );
});
