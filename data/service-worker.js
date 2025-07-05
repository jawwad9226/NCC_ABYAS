const CACHE_NAME = 'ncc-abyas-v1.2';
const STATIC_CACHE = 'ncc-static-v1.2';
const DYNAMIC_CACHE = 'ncc-dynamic-v1.2';

// Resources to cache for offline use
const STATIC_ASSETS = [
  '/',
  '/static/css/app.css',
  '/static/js/app.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  // Add other critical static assets
];

// Install Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch(err => console.log('Cache failed:', err))
  );
  self.skipWaiting();
});

// Activate Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== STATIC_CACHE && cache !== DYNAMIC_CACHE) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch Event - Network First with Fallback Strategy
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle different types of requests
  if (request.method === 'GET') {
    if (isStaticAsset(request.url)) {
      // Cache First Strategy for static assets
      event.respondWith(cacheFirst(request));
    } else if (isApiRequest(request.url)) {
      // Network First Strategy for API calls with offline fallback
      event.respondWith(networkFirstWithOfflineSupport(request));
    } else {
      // Stale While Revalidate for other content
      event.respondWith(staleWhileRevalidate(request));
    }
  } else if (request.method === 'POST') {
    // Handle POST requests for offline functionality
    event.respondWith(handlePostRequest(request));
  }
});

// Cache First Strategy
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.log('Cache first failed:', error);
    return new Response('Offline - Content not available', { status: 503 });
  }
}

// Network First with Offline Support
async function networkFirstWithOfflineSupport(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful API responses
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('Network request failed, trying cache:', error);
    
    // Try to get from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API calls
    return createOfflineApiResponse(request);
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// Handle POST requests for offline functionality
async function handlePostRequest(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Store POST request for later sync
    await storeOfflineRequest(request);
    return new Response(
      JSON.stringify({
        success: true,
        offline: true,
        message: 'Request stored for sync when online'
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Store offline requests for background sync
async function storeOfflineRequest(request) {
  const requestData = {
    url: request.url,
    method: request.method,
    headers: [...request.headers.entries()],
    body: await request.text(),
    timestamp: Date.now()
  };
  
  // Store in IndexedDB for persistence
  const db = await openDB();
  const tx = db.transaction(['offline_requests'], 'readwrite');
  await tx.objectStore('offline_requests').add(requestData);
}

// Create offline API response
function createOfflineApiResponse(request) {
  const url = new URL(request.url);
  
  if (url.pathname.includes('/chat')) {
    return new Response(
      JSON.stringify({
        error: 'You are currently offline. Your message will be sent when connection is restored.',
        offline: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
  
  if (url.pathname.includes('/quiz')) {
    return new Response(
      JSON.stringify({
        questions: getOfflineQuizQuestions(),
        offline: true,
        message: 'Offline quiz mode - results will sync when online'
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
  
  return new Response(
    JSON.stringify({
      error: 'Service temporarily unavailable - please try again when online',
      offline: true
    }),
    {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}

// Helper functions
function isStaticAsset(url) {
  return url.includes('/static/') || 
         url.includes('.css') || 
         url.includes('.js') || 
         url.includes('.woff') || 
         url.includes('.woff2') ||
         url.includes('fonts.googleapis.com');
}

function isApiRequest(url) {
  return url.includes('/api/') || 
         url.includes('generativelanguage.googleapis.com') ||
         url.includes('/chat') ||
         url.includes('/quiz');
}

// IndexedDB helper
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('NCCAbyas', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('offline_requests')) {
        const store = db.createObjectStore('offline_requests', { 
          keyPath: 'id', 
          autoIncrement: true 
        });
        store.createIndex('timestamp', 'timestamp');
      }
      
      if (!db.objectStoreNames.contains('offline_data')) {
        const store = db.createObjectStore('offline_data', { keyPath: 'key' });
      }
    };
  });
}

// Offline quiz questions fallback
function getOfflineQuizQuestions() {
  return [
    {
      question: "What does NCC stand for?",
      options: [
        "National Cadet Corps",
        "National Civil Corps", 
        "Naval Cadet Corps",
        "National Community Corps"
      ],
      correct: 0,
      explanation: "NCC stands for National Cadet Corps, established in 1948."
    },
    {
      question: "What is the NCC motto?",
      options: [
        "Unity and Discipline",
        "Service and Sacrifice", 
        "Discipline and Unity",
        "Honor and Duty"
      ],
      correct: 0,
      explanation: "The NCC motto is 'Unity and Discipline'."
    },
    {
      question: "NCC was established in which year?",
      options: [
        "1947",
        "1948",
        "1949", 
        "1950"
      ],
      correct: 1,
      explanation: "NCC was established on 15 July 1948."
    }
  ];
}

// Background Sync
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(syncOfflineRequests());
  }
});

// Sync offline requests when back online
async function syncOfflineRequests() {
  const db = await openDB();
  const tx = db.transaction(['offline_requests'], 'readonly');
  const requests = await tx.objectStore('offline_requests').getAll();
  
  for (const requestData of requests) {
    try {
      const response = await fetch(requestData.url, {
        method: requestData.method,
        headers: new Headers(requestData.headers),
        body: requestData.body
      });
      
      if (response.ok) {
        // Remove synced request
        const deleteTx = db.transaction(['offline_requests'], 'readwrite');
        await deleteTx.objectStore('offline_requests').delete(requestData.id);
      }
    } catch (error) {
      console.log('Failed to sync request:', error);
    }
  }
}

console.log('NCC ABYAS Service Worker: Enhanced offline functionality loaded');
