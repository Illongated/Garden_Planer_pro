import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Plus, 
  MoreHorizontal, 
  Calendar, 
  User, 
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  Play,
  Pause,
  Flag
} from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { api } from '@/lib/api';
import { Task, TaskStatus, TaskPriority, KanbanBoard as KanbanBoardType } from '../types';

interface KanbanBoardProps {
  projectId: number;
  className?: string;
}

interface TaskCardProps {
  task: Task;
  onUpdate: (taskId: number, updates: Partial<Task>) => void;
  onDelete: (taskId: number) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState(task);

  const handleSave = async () => {
    try {
      await api.put(`/api/v1/project-management/tasks/${task.id}`, editedTask);
      onUpdate(task.id, editedTask);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      try {
        await api.delete(`/api/v1/project-management/tasks/${task.id}`);
        onDelete(task.id);
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.CRITICAL:
        return 'bg-red-500';
      case TaskPriority.HIGH:
        return 'bg-orange-500';
      case TaskPriority.MEDIUM:
        return 'bg-yellow-500';
      case TaskPriority.LOW:
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.DONE:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case TaskStatus.BLOCKED:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case TaskStatus.IN_PROGRESS:
        return <Play className="h-4 w-4 text-blue-500" />;
      case TaskStatus.REVIEW:
        return <Pause className="h-4 w-4 text-yellow-500" />;
      case TaskStatus.TESTING:
        return <Flag className="h-4 w-4 text-purple-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (isEditing) {
    return (
      <Card className="mb-3">
        <CardContent className="p-4">
          <div className="space-y-3">
            <Input
              value={editedTask.title}
              onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
              placeholder="Task title"
            />
            <Textarea
              value={editedTask.description || ''}
              onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
              placeholder="Task description"
              rows={3}
            />
            <div className="flex space-x-2">
              <Select
                value={editedTask.priority}
                onValueChange={(value) => setEditedTask({ ...editedTask, priority: value as TaskPriority })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={TaskPriority.LOW}>Low</SelectItem>
                  <SelectItem value={TaskPriority.MEDIUM}>Medium</SelectItem>
                  <SelectItem value={TaskPriority.HIGH}>High</SelectItem>
                  <SelectItem value={TaskPriority.CRITICAL}>Critical</SelectItem>
                </SelectContent>
              </Select>
              <Button size="sm" onClick={handleSave}>
                Save
              </Button>
              <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-3 hover:shadow-md transition-shadow cursor-pointer">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {getStatusIcon(task.status)}
              <h4 className="font-medium text-sm">{task.title}</h4>
            </div>
            {task.description && (
              <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                {task.description}
              </p>
            )}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {task.priority}
                </Badge>
                {task.assigned_user && (
                  <div className="flex items-center space-x-1">
                    <User className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      {task.assigned_user.full_name || task.assigned_user.email}
                    </span>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${getPriorityColor(task.priority)}`} />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsEditing(true)}
                >
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </div>
            </div>
            {task.tags && task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {task.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const Column: React.FC<{
  title: string;
  status: TaskStatus;
  tasks: Task[];
  onUpdateTask: (taskId: number, updates: Partial<Task>) => void;
  onDeleteTask: (taskId: number) => void;
  onAddTask: (status: TaskStatus) => void;
}> = ({ title, status, tasks, onUpdateTask, onDeleteTask, onAddTask }) => {
  return (
    <div className="flex-1 min-w-0">
      <div className="bg-muted/50 rounded-lg p-4 h-full">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <h3 className="font-semibold text-sm">{title}</h3>
            <Badge variant="secondary" className="text-xs">
              {tasks.length}
            </Badge>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onAddTask(status)}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <div className="space-y-2">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onUpdate={onUpdateTask}
              onDelete={onDeleteTask}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ projectId, className }) => {
  const { user } = useAuth();
  const [kanbanData, setKanbanData] = useState<KanbanBoardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTaskStatus, setNewTaskStatus] = useState<TaskStatus>(TaskStatus.TODO);

  useEffect(() => {
    fetchKanbanData();
  }, [projectId]);

  const fetchKanbanData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/project-management/projects/${projectId}/kanban`);
      setKanbanData(response.data);
    } catch (err) {
      setError('Failed to load kanban board');
      console.error('Kanban error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = (taskId: number, updates: Partial<Task>) => {
    if (kanbanData) {
      const updatedColumns = { ...kanbanData.columns };
      
      // Find and update the task in the appropriate column
      Object.keys(updatedColumns).forEach((status) => {
        updatedColumns[status] = updatedColumns[status].map((task) =>
          task.id === taskId ? { ...task, ...updates } : task
        );
      });

      setKanbanData({
        ...kanbanData,
        columns: updatedColumns,
      });
    }
  };

  const handleDeleteTask = (taskId: number) => {
    if (kanbanData) {
      const updatedColumns = { ...kanbanData.columns };
      
      // Remove the task from all columns
      Object.keys(updatedColumns).forEach((status) => {
        updatedColumns[status] = updatedColumns[status].filter((task) => task.id !== taskId);
      });

      setKanbanData({
        ...kanbanData,
        columns: updatedColumns,
      });
    }
  };

  const handleAddTask = (status: TaskStatus) => {
    setNewTaskStatus(status);
    setShowAddTask(true);
  };

  const handleCreateTask = async (taskData: Partial<Task>) => {
    try {
      const response = await api.post(`/api/v1/project-management/projects/${projectId}/tasks`, {
        ...taskData,
        status: newTaskStatus,
      });

      const newTask = response.data;
      
      if (kanbanData) {
        const updatedColumns = { ...kanbanData.columns };
        updatedColumns[newTaskStatus] = [...updatedColumns[newTaskStatus], newTask];
        
        setKanbanData({
          ...kanbanData,
          columns: updatedColumns,
        });
      }

      setShowAddTask(false);
    } catch (error) {
      console.error('Failed to create task:', error);
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
            onClick={fetchKanbanData} 
            variant="outline" 
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!kanbanData) {
    return null;
  }

  const columns = [
    { title: 'To Do', status: TaskStatus.TODO },
    { title: 'In Progress', status: TaskStatus.IN_PROGRESS },
    { title: 'Review', status: TaskStatus.REVIEW },
    { title: 'Testing', status: TaskStatus.TESTING },
    { title: 'Done', status: TaskStatus.DONE },
    { title: 'Blocked', status: TaskStatus.BLOCKED },
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Kanban Board</h2>
        <Button onClick={() => handleAddTask(TaskStatus.TODO)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </Button>
      </div>

      <div className="flex space-x-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <Column
            key={column.status}
            title={column.title}
            status={column.status}
            tasks={kanbanData.columns[column.status] || []}
            onUpdateTask={handleUpdateTask}
            onDeleteTask={handleDeleteTask}
            onAddTask={handleAddTask}
          />
        ))}
      </div>

      {/* Add Task Dialog */}
      <Dialog open={showAddTask} onOpenChange={setShowAddTask}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Task</DialogTitle>
          </DialogHeader>
          <AddTaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowAddTask(false)}
            initialStatus={newTaskStatus}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

interface AddTaskFormProps {
  onSubmit: (taskData: Partial<Task>) => void;
  onCancel: () => void;
  initialStatus: TaskStatus;
}

const AddTaskForm: React.FC<AddTaskFormProps> = ({ onSubmit, onCancel, initialStatus }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: TaskPriority.MEDIUM,
    status: initialStatus,
    tags: [] as string[],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.title.trim()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Title</label>
        <Input
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Task title"
          required
        />
      </div>
      
      <div>
        <label className="text-sm font-medium">Description</label>
        <Textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Task description"
          rows={3}
        />
      </div>

      <div>
        <label className="text-sm font-medium">Priority</label>
        <Select
          value={formData.priority}
          onValueChange={(value) => setFormData({ ...formData, priority: value as TaskPriority })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={TaskPriority.LOW}>Low</SelectItem>
            <SelectItem value={TaskPriority.MEDIUM}>Medium</SelectItem>
            <SelectItem value={TaskPriority.HIGH}>High</SelectItem>
            <SelectItem value={TaskPriority.CRITICAL}>Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex space-x-2">
        <Button type="submit" disabled={!formData.title.trim()}>
          Create Task
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}; 