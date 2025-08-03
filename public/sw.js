// Service Worker for Garden Planner Pro
// Version: 1.0.0

const CACHE_NAME = 'garden-planner-v1.0.0';
const STATIC_CACHE_NAME = 'garden-planner-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'garden-planner-dynamic-v1.0.0';
const API_CACHE_NAME = 'garden-planner-api-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/v1/plant-catalog/',
  '/api/v1/gardens/',
  '/api/v1/plants/'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker installed');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker install failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== API_CACHE_NAME) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets
  if (isStaticAsset(url.pathname)) {
    event.respondWith(handleStaticAsset(request));
    return;
  }

  // Handle HTML pages
  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(handleHtmlRequest(request));
    return;
  }

  // Default: network first, cache fallback
  event.respondWith(handleDefaultRequest(request));
});

// Handle API requests with cache-first strategy
async function handleApiRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Check if cache is fresh (less than 1 hour old)
      const cacheTime = new Date(cachedResponse.headers.get('sw-cache-time'));
      const now = new Date();
      const cacheAge = now - cacheTime;
      
      if (cacheAge < 3600000) { // 1 hour
        return cachedResponse;
      }
    }

    // Fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Clone response for caching
      const responseToCache = networkResponse.clone();
      
      // Add cache timestamp
      const headers = new Headers(responseToCache.headers);
      headers.append('sw-cache-time', new Date().toISOString());
      
      const responseWithTimestamp = new Response(
        await responseToCache.arrayBuffer(),
        {
          status: responseToCache.status,
          statusText: responseToCache.statusText,
          headers: headers
        }
      );

      // Cache the response
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, responseWithTimestamp);
    }

    return networkResponse;
  } catch (error) {
    // Fallback to cache if network fails
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response
    return new Response(
      JSON.stringify({ error: 'Offline - No cached data available' }),
      { 
        status: 503, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Asset not available offline', { status: 404 });
  }
}

// Handle HTML requests with network-first strategy
async function handleHtmlRequest(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    return caches.match('/offline.html');
  }
}

// Handle default requests with network-first strategy
async function handleDefaultRequest(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Resource not available offline', { status: 404 });
  }
}

// Check if URL is a static asset
function isStaticAsset(pathname) {
  const staticExtensions = [
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
    '.woff', '.woff2', '.ttf', '.eot', '.ico'
  ];
  
  return staticExtensions.some(ext => pathname.endsWith(ext));
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Background sync implementation
async function doBackgroundSync() {
  try {
    // Get stored offline actions
    const offlineActions = await getOfflineActions();
    
    for (const action of offlineActions) {
      try {
        const response = await fetch(action.url, {
          method: action.method,
          headers: action.headers,
          body: action.body
        });
        
        if (response.ok) {
          // Remove successful action from storage
          await removeOfflineAction(action.id);
        }
      } catch (error) {
        console.error('Background sync failed for action:', action.id, error);
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Store offline action
async function storeOfflineAction(action) {
  const actions = await getOfflineActions();
  actions.push({
    id: Date.now().toString(),
    ...action,
    timestamp: Date.now()
  });
  
  localStorage.setItem('offline-actions', JSON.stringify(actions));
}

// Get stored offline actions
async function getOfflineActions() {
  const stored = localStorage.getItem('offline-actions');
  return stored ? JSON.parse(stored) : [];
}

// Remove offline action
async function removeOfflineAction(actionId) {
  const actions = await getOfflineActions();
  const filteredActions = actions.filter(action => action.id !== actionId);
  localStorage.setItem('offline-actions', JSON.stringify(filteredActions));
}

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_API_RESPONSE') {
    event.waitUntil(
      caches.open(API_CACHE_NAME)
        .then(cache => cache.put(event.data.request, event.data.response))
    );
  }
}); 