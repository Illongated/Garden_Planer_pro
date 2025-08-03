import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Plus, 
  BarChart3, 
  Kanban, 
  Bug, 
  MessageSquare, 
  GitBranch,
  Settings,
  Users,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { api } from '@/lib/api';
import { Dashboard } from '../components/Dashboard';
import { KanbanBoard } from '../components/KanbanBoard';
import { Project, ProjectStatus, ProjectCreate } from '../types';

interface ProjectManagementPageProps {
  className?: string;
}

export const ProjectManagementPage: React.FC<ProjectManagementPageProps> = ({ className }) => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/project-management/projects');
      const projectList = response.data.projects;
      setProjects(projectList);
      
      // Select the first project by default
      if (projectList.length > 0 && !selectedProject) {
        setSelectedProject(projectList[0]);
      }
    } catch (err) {
      setError('Failed to load projects');
      console.error('Projects error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (projectData: ProjectCreate) => {
    try {
      const response = await api.post('/api/v1/project-management/projects', projectData);
      const newProject = response.data;
      setProjects([...projects, newProject]);
      setSelectedProject(newProject);
      setShowCreateProject(false);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const getStatusIcon = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.IN_PROGRESS:
        return <Clock className="h-4 w-4 text-blue-500" />;
      case ProjectStatus.REVIEW:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case ProjectStatus.TESTING:
        return <CheckCircle className="h-4 w-4 text-purple-500" />;
      case ProjectStatus.DEPLOYED:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case ProjectStatus.ARCHIVED:
        return <Settings className="h-4 w-4 text-gray-500" />;
      default:
        return <Calendar className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusVariant = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.IN_PROGRESS:
        return 'default';
      case ProjectStatus.REVIEW:
        return 'secondary';
      case ProjectStatus.TESTING:
        return 'outline';
      case ProjectStatus.DEPLOYED:
        return 'default';
      case ProjectStatus.ARCHIVED:
        return 'destructive';
      default:
        return 'outline';
    }
  };

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
          <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
          <p className="text-destructive">{error}</p>
          <Button 
            onClick={fetchProjects} 
            variant="outline" 
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Project Management</h1>
          <p className="text-muted-foreground">
            Manage your projects, tasks, and team collaboration
          </p>
        </div>
        <Dialog open={showCreateProject} onOpenChange={setShowCreateProject}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
            </DialogHeader>
            <CreateProjectForm onSubmit={handleCreateProject} onCancel={() => setShowCreateProject(false)} />
          </DialogContent>
        </Dialog>
      </div>

      {/* Project Selection */}
      {projects.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-semibold">Select Project:</h2>
            <Select
              value={selectedProject?.id.toString()}
              onValueChange={(value) => {
                const project = projects.find(p => p.id.toString() === value);
                setSelectedProject(project || null);
              }}
            >
              <SelectTrigger className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id.toString()}>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(project.status)}
                      <span>{project.name}</span>
                      <Badge variant={getStatusVariant(project.status)} className="ml-auto">
                        {project.status}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {selectedProject && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(selectedProject.status)}
                    <div>
                      <CardTitle>{selectedProject.name}</CardTitle>
                      <CardDescription>{selectedProject.description}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusVariant(selectedProject.status)}>
                      {selectedProject.status}
                    </Badge>
                    <div className="text-sm text-muted-foreground">
                      {selectedProject.progress.toFixed(1)}% complete
                    </div>
                  </div>
                </div>
              </CardHeader>
            </Card>
          )}
        </div>
      )}

      {/* No Projects State */}
      {projects.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GitBranch className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first project to get started with project management
            </p>
            <Button onClick={() => setShowCreateProject(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create First Project
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Project Content */}
      {selectedProject && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="kanban" className="flex items-center space-x-2">
              <Kanban className="h-4 w-4" />
              <span>Kanban</span>
            </TabsTrigger>
            <TabsTrigger value="bugs" className="flex items-center space-x-2">
              <Bug className="h-4 w-4" />
              <span>Bugs</span>
            </TabsTrigger>
            <TabsTrigger value="feedback" className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Feedback</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-4">
            <Dashboard />
          </TabsContent>

          <TabsContent value="kanban" className="space-y-4">
            <KanbanBoard projectId={selectedProject.id} />
          </TabsContent>

          <TabsContent value="bugs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Bug Tracking</CardTitle>
                <CardDescription>
                  Track and manage bugs for {selectedProject.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Bug tracking functionality will be implemented here.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="feedback" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>User Feedback</CardTitle>
                <CardDescription>
                  Manage user feedback and feature requests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Feedback management functionality will be implemented here.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Project Analytics</CardTitle>
                <CardDescription>
                  Detailed analytics and insights for {selectedProject.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Analytics functionality will be implemented here.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

interface CreateProjectFormProps {
  onSubmit: (projectData: ProjectCreate) => void;
  onCancel: () => void;
}

const CreateProjectForm: React.FC<CreateProjectFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: ProjectStatus.PLANNING,
    due_date: '',
    progress: 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Project Name</label>
        <Input
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Enter project name"
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium">Description</label>
        <Textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Enter project description"
          rows={3}
        />
      </div>

      <div>
        <label className="text-sm font-medium">Status</label>
        <Select
          value={formData.status}
          onValueChange={(value) => setFormData({ ...formData, status: value as ProjectStatus })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ProjectStatus.PLANNING}>Planning</SelectItem>
            <SelectItem value={ProjectStatus.IN_PROGRESS}>In Progress</SelectItem>
            <SelectItem value={ProjectStatus.REVIEW}>Review</SelectItem>
            <SelectItem value={ProjectStatus.TESTING}>Testing</SelectItem>
            <SelectItem value={ProjectStatus.DEPLOYED}>Deployed</SelectItem>
            <SelectItem value={ProjectStatus.ARCHIVED}>Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Due Date</label>
        <Input
          type="date"
          value={formData.due_date}
          onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
        />
      </div>

      <div className="flex space-x-2">
        <Button type="submit" disabled={!formData.name.trim()}>
          Create Project
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}; 