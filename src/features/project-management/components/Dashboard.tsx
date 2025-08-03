import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  Bug, 
  CheckCircle, 
  Clock, 
  Code, 
  GitBranch, 
  Globe, 
  Users, 
  TrendingUp,
  AlertTriangle,
  Activity,
  Calendar
} from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { api } from '@/lib/api';
import { DashboardMetrics, ProjectProgress } from '../types';

interface DashboardProps {
  className?: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [projectProgress, setProjectProgress] = useState<ProjectProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [metricsResponse, progressResponse] = await Promise.all([
          api.get('/api/v1/project-management/dashboard/metrics'),
          api.get('/api/v1/project-management/dashboard/progress')
        ]);

        setMetrics(metricsResponse.data);
        setProjectProgress(progressResponse.data);
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-2" />
          <p className="text-destructive">{error}</p>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline" 
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Project Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name || user?.email}
          </p>
        </div>
        <Button>
          <Activity className="h-4 w-4 mr-2" />
          View Analytics
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_projects}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.active_projects} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasks</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_tasks}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.completed_tasks} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Bugs</CardTitle>
            <Bug className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_bugs}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.open_bugs} open, {metrics.critical_bugs} critical
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.active_users}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.total_users} total users
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm">
                <span>API Response Time</span>
                <span>{metrics.average_response_time.toFixed(2)}ms</span>
              </div>
              <Progress 
                value={Math.min((metrics.average_response_time / 1000) * 100, 100)} 
                className="mt-1"
              />
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Test Coverage</span>
                <span>{metrics.test_coverage_avg.toFixed(1)}%</span>
              </div>
              <Progress value={metrics.test_coverage_avg} className="mt-1" />
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Code Quality</span>
                <span>{metrics.code_quality_avg.toFixed(1)}%</span>
              </div>
              <Progress value={metrics.code_quality_avg} className="mt-1" />
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Project Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {projectProgress.map((project) => (
                <div key={project.project_id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium">{project.project_name}</h4>
                      <Badge variant={getStatusVariant(project.status)}>
                        {project.status}
                      </Badge>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {project.progress.toFixed(1)}%
                    </span>
                  </div>
                  <Progress value={project.progress} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>
                      Tasks: {project.tasks_completed}/{project.tasks_total}
                    </span>
                    <span>
                      Bugs: {project.bugs_open} open, {project.bugs_resolved} resolved
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-4 w-4 mr-2" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* This would be populated with real activity data */}
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm">New task created in Project Alpha</p>
                <p className="text-xs text-muted-foreground">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm">Bug report submitted for Project Beta</p>
                <p className="text-xs text-muted-foreground">15 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm">Code review completed for Project Gamma</p>
                <p className="text-xs text-muted-foreground">1 hour ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const getStatusVariant = (status: string) => {
  switch (status) {
    case 'in_progress':
      return 'default';
    case 'review':
      return 'secondary';
    case 'testing':
      return 'outline';
    case 'deployed':
      return 'default';
    case 'archived':
      return 'destructive';
    default:
      return 'outline';
  }
}; 