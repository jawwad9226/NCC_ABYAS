// Enhanced Service Worker for NCC ABYAS
const CACHE_NAME = 'ncc-abyas-v1.2';
const STATIC_CACHE = 'ncc-static-v1.2';
const DYNAMIC_CACHE = 'ncc-dynamic-v1.2';

// Static assets to cache
const STATIC_ASSETS = [
  '/',
  '/data/logo.svg',
  '/data/manifest.json',
  '/data/icon-192.png',
  '/data/icon-512.png'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && 
              cacheName !== DYNAMIC_CACHE &&
              cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategy
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip external requests
  if (!url.origin.includes(self.location.origin)) return;

  // Handle API requests with network-first strategy
  if (url.pathname.includes('/api/') || url.pathname.includes('/_stcore/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request);
        })
    );
    return;
  }

  // Handle static assets with cache-first strategy
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(request)
          .then(response => {
            // Cache the response if successful
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(DYNAMIC_CACHE).then(cache => {
                cache.put(request, responseClone);
              });
            }
            return response;
          });
      })
      .catch(() => {
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Handle offline data sync
      syncOfflineData()
    );
  }
});

// Push notifications
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/data/icon-192.png',
      badge: '/data/badge.png',
      vibrate: [100, 50, 100],
      data: data.data,
      actions: [
        {
          action: 'open',
          title: 'Open App',
          icon: '/data/open-icon.png'
        },
        {
          action: 'close',
          title: 'Close',
          icon: '/data/close-icon.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function for offline data sync
async function syncOfflineData() {
  try {
    // Implement your offline data synchronization logic here
    console.log('Syncing offline data...');
    
    // Example: sync chat history, quiz results, etc.
    const offlineData = await getOfflineData();
    if (offlineData.length > 0) {
      await syncToServer(offlineData);
      await clearOfflineData();
    }
  } catch (error) {
    console.error('Sync failed:', error);
  }
}

async function getOfflineData() {
  // Implement logic to retrieve offline data
  return [];
}

async function syncToServer(data) {
  // Implement logic to sync data to server
  console.log('Syncing to server:', data);
}

async function clearOfflineData() {
  // Implement logic to clear synced offline data
  console.log('Clearing offline data');
}
