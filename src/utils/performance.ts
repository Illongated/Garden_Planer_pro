// Performance Monitoring Utility
// Version: 1.0.0

// Import web-vitals with proper error handling
let webVitals: any = null;

// Dynamic import for web-vitals
(async () => {
  try {
    webVitals = await import('web-vitals');
  } catch (error) {
    console.warn('web-vitals not available, performance monitoring limited');
  }
})();

interface PerformanceMetrics {
  cls: number;
  fid: number;
  fcp: number;
  lcp: number;
  ttfb: number;
  timestamp: number;
}

interface PerformanceConfig {
  endpoint: string;
  sampleRate: number;
  debug: boolean;
}

class PerformanceMonitor {
  private config: PerformanceConfig;
  private metrics: Partial<PerformanceMetrics> = {};
  private observers: Set<(metrics: PerformanceMetrics) => void> = new Set();

  constructor(config: Partial<PerformanceConfig> = {}) {
    this.config = {
      endpoint: '/api/v1/performance/metrics',
      sampleRate: 1.0, // 100% sample rate
      debug: false,
      ...config
    };

    this.initializeMetrics();
  }

  /**
   * Initialize performance metrics collection
   */
  private initializeMetrics(): void {
    // Only collect metrics for a percentage of users
    if (Math.random() > this.config.sampleRate) {
      return;
    }

    // Collect Core Web Vitals if available
    if (webVitals) {
      webVitals.getCLS(this.handleCLS.bind(this));
      webVitals.getFID(this.handleFID.bind(this));
      webVitals.getFCP(this.handleFCP.bind(this));
      webVitals.getLCP(this.handleLCP.bind(this));
      webVitals.getTTFB(this.handleTTFB.bind(this));
    }

    // Additional performance monitoring
    this.monitorMemoryUsage();
    this.monitorNetworkRequests();
    this.monitorLongTasks();
  }

  /**
   * Handle Cumulative Layout Shift
   */
  private handleCLS(metric: any): void {
    this.metrics.cls = metric.value;
    this.checkMetricsComplete();
  }

  /**
   * Handle First Input Delay
   */
  private handleFID(metric: any): void {
    this.metrics.fid = metric.value;
    this.checkMetricsComplete();
  }

  /**
   * Handle First Contentful Paint
   */
  private handleFCP(metric: any): void {
    this.metrics.fcp = metric.value;
    this.checkMetricsComplete();
  }

  /**
   * Handle Largest Contentful Paint
   */
  private handleLCP(metric: any): void {
    this.metrics.lcp = metric.value;
    this.checkMetricsComplete();
  }

  /**
   * Handle Time to First Byte
   */
  private handleTTFB(metric: any): void {
    this.metrics.ttfb = metric.value;
    this.checkMetricsComplete();
  }

  /**
   * Check if all metrics are collected
   */
  private checkMetricsComplete(): void {
    const requiredMetrics = ['cls', 'fid', 'fcp', 'lcp', 'ttfb'];
    const hasAllMetrics = requiredMetrics.every(metric => 
      this.metrics[metric as keyof PerformanceMetrics] !== undefined
    );

    if (hasAllMetrics) {
      const completeMetrics: PerformanceMetrics = {
        cls: this.metrics.cls!,
        fid: this.metrics.fid!,
        fcp: this.metrics.fcp!,
        lcp: this.metrics.lcp!,
        ttfb: this.metrics.ttfb!,
        timestamp: Date.now()
      };

      this.notifyObservers(completeMetrics);
      this.sendMetrics(completeMetrics);
    }
  }

  /**
   * Monitor memory usage
   */
  private monitorMemoryUsage(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      
      setInterval(() => {
        const memoryMetrics = {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
          timestamp: Date.now()
        };

        if (this.config.debug) {
          console.log('Memory usage:', memoryMetrics);
        }

        // Alert if memory usage is high
        const usagePercentage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
        if (usagePercentage > 0.8) {
          console.warn('High memory usage detected:', usagePercentage * 100, '%');
        }
      }, 30000); // Check every 30 seconds
    }
  }

  /**
   * Monitor network requests
   */
  private monitorNetworkRequests(): void {
    const originalFetch = window.fetch;
    const requests: any[] = [];

    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = typeof args[0] === 'string' ? args[0] : (args[0] as Request).url;

      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        const duration = endTime - startTime;

        requests.push({
          url,
          duration,
          status: response.status,
          timestamp: Date.now()
        });

        // Keep only last 100 requests
        if (requests.length > 100) {
          requests.splice(0, requests.length - 100);
        }

        // Alert on slow requests
        if (duration > 5000) { // 5 seconds
          console.warn('Slow request detected:', url, duration, 'ms');
        }

        return response;
      } catch (error) {
        const endTime = performance.now();
        const duration = endTime - startTime;

        requests.push({
          url,
          duration,
          error: true,
          timestamp: Date.now()
        });

        throw error;
      }
    };
  }

  /**
   * Monitor long tasks
   */
  private monitorLongTasks(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const longTask = entry as PerformanceEntry;
          
          if (longTask.duration > 50) { // 50ms threshold
            console.warn('Long task detected:', {
              duration: longTask.duration,
              name: longTask.name,
              startTime: longTask.startTime
            });
          }
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
    }
  }

  /**
   * Send metrics to server
   */
  private async sendMetrics(metrics: PerformanceMetrics): Promise<void> {
    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...metrics,
          userAgent: navigator.userAgent,
          url: window.location.href,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      if (this.config.debug) {
        console.log('Performance metrics sent successfully');
      }
    } catch (error) {
      console.error('Failed to send performance metrics:', error);
    }
  }

  /**
   * Add observer for metrics
   */
  addObserver(callback: (metrics: PerformanceMetrics) => void): void {
    this.observers.add(callback);
  }

  /**
   * Remove observer
   */
  removeObserver(callback: (metrics: PerformanceMetrics) => void): void {
    this.observers.delete(callback);
  }

  /**
   * Notify all observers
   */
  private notifyObservers(metrics: PerformanceMetrics): void {
    this.observers.forEach(callback => {
      try {
        callback(metrics);
      } catch (error) {
        console.error('Error in performance observer:', error);
      }
    });
  }

  /**
   * Get current metrics
   */
  getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }

  /**
   * Measure custom performance
   */
  measure(name: string, fn: () => void | Promise<void>): void {
    const startTime = performance.now();
    
    try {
      const result = fn();
      
      if (result instanceof Promise) {
        result.finally(() => {
          const endTime = performance.now();
          const duration = endTime - startTime;
          
          if (this.config.debug) {
            console.log(`Custom measurement '${name}':`, duration, 'ms');
          }
          
          // Send custom measurement
          this.sendCustomMeasurement(name, duration);
        });
      } else {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        if (this.config.debug) {
          console.log(`Custom measurement '${name}':`, duration, 'ms');
        }
        
        // Send custom measurement
        this.sendCustomMeasurement(name, duration);
      }
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      console.error(`Error in custom measurement '${name}':`, error);
      this.sendCustomMeasurement(name, duration, error);
    }
  }

  /**
   * Send custom measurement
   */
  private async sendCustomMeasurement(name: string, duration: number, error?: any): Promise<void> {
    try {
      await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'custom',
          name,
          duration,
          error: error?.message,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('Failed to send custom measurement:', error);
    }
  }

  /**
   * Get performance budget
   */
  getPerformanceBudget(): Record<string, number> {
    return {
      cls: 0.1,      // Cumulative Layout Shift
      fid: 100,      // First Input Delay (ms)
      fcp: 1800,     // First Contentful Paint (ms)
      lcp: 2500,     // Largest Contentful Paint (ms)
      ttfb: 800      // Time to First Byte (ms)
    };
  }

  /**
   * Check if metrics meet performance budget
   */
  checkPerformanceBudget(metrics: PerformanceMetrics): Record<string, boolean> {
    const budget = this.getPerformanceBudget();
    
    return {
      cls: metrics.cls <= budget.cls,
      fid: metrics.fid <= budget.fid,
      fcp: metrics.fcp <= budget.fcp,
      lcp: metrics.lcp <= budget.lcp,
      ttfb: metrics.ttfb <= budget.ttfb
    };
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor({
  debug: typeof window !== 'undefined' && window.location.hostname === 'localhost'
});

export default performanceMonitor; 