// Service Worker Registration and Management
// Version: 1.0.0

interface ServiceWorkerMessage {
  type: string;
  data?: any;
}

class ServiceWorkerManager {
  private swRegistration: ServiceWorkerRegistration | null = null;
  private isSupported: boolean;

  constructor() {
    this.isSupported = 'serviceWorker' in navigator;
  }

  /**
   * Register the service worker
   */
  async register(): Promise<boolean> {
    if (!this.isSupported) {
      console.warn('Service Worker not supported');
      return false;
    }

    try {
      this.swRegistration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('Service Worker registered successfully:', this.swRegistration);

      // Handle updates
      this.swRegistration.addEventListener('updatefound', () => {
        const newWorker = this.swRegistration!.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker available
              this.showUpdateNotification();
            }
          });
        }
      });

      // Handle controller change
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        console.log('Service Worker controller changed');
        window.location.reload();
      });

      return true;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return false;
    }
  }

  /**
   * Unregister the service worker
   */
  async unregister(): Promise<boolean> {
    if (!this.swRegistration) {
      return false;
    }

    try {
      const unregistered = await this.swRegistration.unregister();
      console.log('Service Worker unregistered:', unregistered);
      return unregistered;
    } catch (error) {
      console.error('Service Worker unregistration failed:', error);
      return false;
    }
  }

  /**
   * Send message to service worker
   */
  async sendMessage(message: ServiceWorkerMessage): Promise<void> {
    if (!this.swRegistration || !this.swRegistration.active) {
      console.warn('Service Worker not active');
      return;
    }

    try {
      await this.swRegistration.active.postMessage(message);
    } catch (error) {
      console.error('Failed to send message to Service Worker:', error);
    }
  }

  /**
   * Cache API response
   */
  async cacheApiResponse(request: Request, response: Response): Promise<void> {
    await this.sendMessage({
      type: 'CACHE_API_RESPONSE',
      data: { request, response }
    });
  }

  /**
   * Check if service worker is active
   */
  isActive(): boolean {
    return !!this.swRegistration?.active;
  }

  /**
   * Get service worker registration
   */
  getRegistration(): ServiceWorkerRegistration | null {
    return this.swRegistration;
  }

  /**
   * Show update notification
   */
  private showUpdateNotification(): void {
    // You can implement a custom notification UI here
    if (confirm('A new version is available. Would you like to update?')) {
      this.updateServiceWorker();
    }
  }

  /**
   * Update service worker
   */
  private updateServiceWorker(): void {
    if (this.swRegistration?.waiting) {
      this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
  }

  /**
   * Check for updates
   */
  async checkForUpdates(): Promise<void> {
    if (this.swRegistration) {
      await this.swRegistration.update();
    }
  }

  /**
   * Get cache information
   */
  async getCacheInfo(): Promise<{ name: string; size: number }[]> {
    if (!this.isSupported) {
      return [];
    }

    try {
      const cacheNames = await caches.keys();
      const cacheInfo = await Promise.all(
        cacheNames.map(async (name) => {
          const cache = await caches.open(name);
          const keys = await cache.keys();
          return {
            name,
            size: keys.length
          };
        })
      );

      return cacheInfo;
    } catch (error) {
      console.error('Failed to get cache info:', error);
      return [];
    }
  }

  /**
   * Clear all caches
   */
  async clearAllCaches(): Promise<void> {
    if (!this.isSupported) {
      return;
    }

    try {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );
      console.log('All caches cleared');
    } catch (error) {
      console.error('Failed to clear caches:', error);
    }
  }

  /**
   * Get offline status
   */
  isOffline(): boolean {
    return !navigator.onLine;
  }

  /**
   * Listen for online/offline events
   */
  onOnlineStatusChange(callback: (isOnline: boolean) => void): void {
    window.addEventListener('online', () => callback(true));
    window.addEventListener('offline', () => callback(false));
  }
}

// Create singleton instance
const serviceWorkerManager = new ServiceWorkerManager();

export default serviceWorkerManager; 