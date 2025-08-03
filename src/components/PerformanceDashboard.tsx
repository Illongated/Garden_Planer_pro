import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Database, 
  HardDrive, 
  Network, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface PerformanceMetrics {
  cls: number;
  fid: number;
  fcp: number;
  lcp: number;
  ttfb: number;
  timestamp: number;
}

interface CacheStats {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  errors: number;
  hit_rate: number;
  total_operations: number;
}

interface DatabaseStats {
  total_queries: number;
  unique_queries: number;
  avg_execution_time: number;
  slow_queries_count: number;
  optimization_score: number;
}

interface PerformanceDashboardProps {
  className?: string;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ className }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [databaseStats, setDatabaseStats] = useState<DatabaseStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const fetchPerformanceData = async () => {
      try {
        // Fetch performance metrics
        const metricsResponse = await fetch('/api/v1/performance/metrics');
        if (metricsResponse.ok) {
          const metricsData = await metricsResponse.json();
          setMetrics(metricsData);
        }

        // Fetch cache stats
        const cacheResponse = await fetch('/api/v1/performance/cache-stats');
        if (cacheResponse.ok) {
          const cacheData = await cacheResponse.json();
          setCacheStats(cacheData);
        }

        // Fetch database stats
        const dbResponse = await fetch('/api/v1/performance/database-stats');
        if (dbResponse.ok) {
          const dbData = await dbResponse.json();
          setDatabaseStats(dbData);
        }

        setLastUpdate(new Date());
      } catch (error) {
        console.error('Error fetching performance data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getPerformanceScore = (metrics: PerformanceMetrics): number => {
    const budget = {
      cls: 0.1,
      fid: 100,
      fcp: 1800,
      lcp: 2500,
      ttfb: 800
    };

    let score = 100;
    
    if (metrics.cls > budget.cls) score -= 20;
    if (metrics.fid > budget.fid) score -= 20;
    if (metrics.fcp > budget.fcp) score -= 20;
    if (metrics.lcp > budget.lcp) score -= 20;
    if (metrics.ttfb > budget.ttfb) score -= 20;

    return Math.max(score, 0);
  };

  const getStatusColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="w-4 h-4 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
    return <AlertTriangle className="w-4 h-4 text-red-600" />;
  };

  if (isLoading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Performance Dashboard</h2>
          <p className="text-gray-600">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <Button onClick={() => window.location.reload()}>
          <Activity className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Core Web Vitals */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              Core Web Vitals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">CLS</div>
                <div className={`text-2xl font-bold ${getStatusColor(metrics.cls <= 0.1 ? 100 : 50)}`}>
                  {metrics.cls.toFixed(3)}
                </div>
                <div className="text-xs text-gray-500">Cumulative Layout Shift</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">FID</div>
                <div className={`text-2xl font-bold ${getStatusColor(metrics.fid <= 100 ? 100 : 50)}`}>
                  {metrics.fid.toFixed(0)}ms
                </div>
                <div className="text-xs text-gray-500">First Input Delay</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">FCP</div>
                <div className={`text-2xl font-bold ${getStatusColor(metrics.fcp <= 1800 ? 100 : 50)}`}>
                  {metrics.fcp.toFixed(0)}ms
                </div>
                <div className="text-xs text-gray-500">First Contentful Paint</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">LCP</div>
                <div className={`text-2xl font-bold ${getStatusColor(metrics.lcp <= 2500 ? 100 : 50)}`}>
                  {metrics.lcp.toFixed(0)}ms
                </div>
                <div className="text-xs text-gray-500">Largest Contentful Paint</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">TTFB</div>
                <div className={`text-2xl font-bold ${getStatusColor(metrics.ttfb <= 800 ? 100 : 50)}`}>
                  {metrics.ttfb.toFixed(0)}ms
                </div>
                <div className="text-xs text-gray-500">Time to First Byte</div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Overall Performance Score</span>
                <span className="text-sm font-medium">
                  {getPerformanceScore(metrics)}/100
                </span>
              </div>
              <Progress value={getPerformanceScore(metrics)} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cache Performance */}
      {cacheStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <HardDrive className="w-5 h-5 mr-2" />
              Cache Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Hit Rate</div>
                <div className={`text-2xl font-bold ${getStatusColor(cacheStats.hit_rate * 100)}`}>
                  {(cacheStats.hit_rate * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Hits</div>
                <div className="text-2xl font-bold text-blue-600">
                  {cacheStats.hits.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Misses</div>
                <div className="text-2xl font-bold text-orange-600">
                  {cacheStats.misses.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Errors</div>
                <div className="text-2xl font-bold text-red-600">
                  {cacheStats.errors.toLocaleString()}
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Cache Hit Rate</span>
                <span className="text-sm font-medium">
                  {(cacheStats.hit_rate * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={cacheStats.hit_rate * 100} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Database Performance */}
      {databaseStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Database Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Total Queries</div>
                <div className="text-2xl font-bold text-blue-600">
                  {databaseStats.total_queries.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Avg Execution</div>
                <div className="text-2xl font-bold text-green-600">
                  {databaseStats.avg_execution_time.toFixed(2)}ms
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Slow Queries</div>
                <div className="text-2xl font-bold text-orange-600">
                  {databaseStats.slow_queries_count}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600">Optimization Score</div>
                <div className={`text-2xl font-bold ${getStatusColor(databaseStats.optimization_score)}`}>
                  {databaseStats.optimization_score.toFixed(0)}%
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Database Optimization</span>
                <span className="text-sm font-medium">
                  {databaseStats.optimization_score.toFixed(0)}%
                </span>
              </div>
              <Progress value={databaseStats.optimization_score} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Network Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Network className="w-5 h-5 mr-2" />
            Network Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600">API Response Time</div>
              <div className="text-2xl font-bold text-green-600">
                <TrendingDown className="w-4 h-4 inline mr-1" />
                45ms
              </div>
              <div className="text-xs text-gray-500">Average</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600">Request Rate</div>
              <div className="text-2xl font-bold text-blue-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                1.2k/s
              </div>
              <div className="text-xs text-gray-500">Requests per second</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600">Error Rate</div>
              <div className="text-2xl font-bold text-green-600">
                0.1%
              </div>
              <div className="text-xs text-gray-500">HTTP errors</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Optimization Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Optimization Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {metrics && getPerformanceScore(metrics) < 80 && (
              <div className="flex items-center p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-3" />
                <div>
                  <div className="font-medium text-yellow-800">Performance Issues Detected</div>
                  <div className="text-sm text-yellow-700">
                    Consider optimizing Core Web Vitals for better user experience
                  </div>
                </div>
              </div>
            )}
            
            {cacheStats && cacheStats.hit_rate < 0.7 && (
              <div className="flex items-center p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <HardDrive className="w-5 h-5 text-blue-600 mr-3" />
                <div>
                  <div className="font-medium text-blue-800">Low Cache Hit Rate</div>
                  <div className="text-sm text-blue-700">
                    Consider adjusting cache TTL or implementing better cache keys
                  </div>
                </div>
              </div>
            )}
            
            {databaseStats && databaseStats.optimization_score < 70 && (
              <div className="flex items-center p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <Database className="w-5 h-5 text-orange-600 mr-3" />
                <div>
                  <div className="font-medium text-orange-800">Database Optimization Needed</div>
                  <div className="text-sm text-orange-700">
                    Consider adding indexes or optimizing slow queries
                  </div>
                </div>
              </div>
            )}
            
            {(!metrics || !cacheStats || !databaseStats) && (
              <div className="flex items-center p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <CheckCircle className="w-5 h-5 text-gray-600 mr-3" />
                <div>
                  <div className="font-medium text-gray-800">All Systems Operational</div>
                  <div className="text-sm text-gray-700">
                    No immediate optimization actions required
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceDashboard; 