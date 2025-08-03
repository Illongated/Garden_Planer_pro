export interface DashboardMetrics {
  total_projects: number;
  active_projects: number;
  total_tasks: number;
  completed_tasks: number;
  total_bugs: number;
  open_bugs: number;
  critical_bugs: number;
  total_users: number;
  active_users: number;
  average_response_time: number;
  test_coverage_avg: number;
  code_quality_avg: number;
}

export interface ProjectProgress {
  project_id: number;
  project_name: string;
  progress: number;
  status: ProjectStatus;
  due_date?: string;
  tasks_completed: number;
  tasks_total: number;
  bugs_open: number;
  bugs_resolved: number;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: ProjectStatus;
  owner_id: number;
  created_at: string;
  updated_at?: string;
  due_date?: string;
  progress: number;
  metadata?: Record<string, any>;
  owner: UserSummary;
  collaborators: ProjectCollaborator[];
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: number;
  assigned_to?: number;
  created_by: number;
  created_at: string;
  updated_at?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  tags?: string[];
  assigned_user?: UserSummary;
  creator: UserSummary;
}

export interface Bug {
  id: number;
  title: string;
  description?: string;
  severity: BugSeverity;
  status: TaskStatus;
  project_id: number;
  reported_by: number;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
  reporter: UserSummary;
  assigned_user?: UserSummary;
}

export interface Feedback {
  id: number;
  user_id: number;
  project_id: number;
  category: string;
  title: string;
  description?: string;
  rating?: number;
  status: string;
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
  tags?: string[];
  user: UserSummary;
}

export interface Release {
  id: number;
  project_id: number;
  version: string;
  title: string;
  description?: string;
  release_notes?: string;
  status: string;
  created_by: number;
  created_at: string;
  deployed_at?: string;
  changes?: Record<string, any>[];
  creator: UserSummary;
}

export interface CodeReview {
  id: number;
  project_id: number;
  reviewer_id: number;
  author_id: number;
  pull_request_url?: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  review_data?: Record<string, any>;
  reviewer: UserSummary;
  author: UserSummary;
}

export interface ProjectCollaborator {
  id: number;
  user: UserSummary;
  role: string;
  joined_at: string;
}

export interface UserSummary {
  id: number;
  email: string;
  full_name?: string;
}

export interface ProjectMetrics {
  id: number;
  project_id: number;
  date: string;
  lines_of_code: number;
  test_coverage: number;
  code_quality_score: number;
  build_success_rate: number;
  api_response_time_avg: number;
  api_response_time_p95: number;
  frontend_load_time: number;
  memory_usage: number;
  cpu_usage: number;
  active_users: number;
  new_users: number;
  feature_adoption_rate: number;
  bugs_total: number;
  bugs_open: number;
  bugs_resolved: number;
  bugs_critical: number;
  tasks_total: number;
  tasks_completed: number;
  tasks_in_progress: number;
  tasks_overdue: number;
}

export interface UserActivity {
  id: number;
  user_id: number;
  project_id: number;
  activity_type: string;
  activity_data?: Record<string, any>;
  timestamp: string;
  session_id?: string;
  user: UserSummary;
}

export interface ProjectAnalytics {
  project_id: number;
  project_name: string;
  metrics: ProjectMetrics;
  recent_activities: UserActivity[];
  top_contributors: UserSummary[];
  recent_feedback: Feedback[];
}

export interface KanbanBoard {
  project_id: number;
  columns: Record<string, Task[]>;
}

// Enums
export enum ProjectStatus {
  PLANNING = 'planning',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  TESTING = 'testing',
  DEPLOYED = 'deployed',
  ARCHIVED = 'archived'
}

export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  TESTING = 'testing',
  DONE = 'done',
  BLOCKED = 'blocked'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum BugSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// API Response Types
export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  size: number;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  size: number;
}

export interface BugListResponse {
  bugs: Bug[];
  total: number;
  page: number;
  size: number;
}

export interface FeedbackListResponse {
  feedback: Feedback[];
  total: number;
  page: number;
  size: number;
}

export interface ReleaseListResponse {
  releases: Release[];
  total: number;
  page: number;
  size: number;
}

export interface CodeReviewListResponse {
  reviews: CodeReview[];
  total: number;
  page: number;
  size: number;
}

// Form Types
export interface ProjectCreate {
  name: string;
  description?: string;
  status?: ProjectStatus;
  due_date?: string;
  progress?: number;
  metadata?: Record<string, any>;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  due_date?: string;
  progress?: number;
  metadata?: Record<string, any>;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  project_id: number;
  assigned_to?: number;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_to?: number;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  tags?: string[];
}

export interface BugCreate {
  title: string;
  description?: string;
  severity?: BugSeverity;
  status?: TaskStatus;
  project_id: number;
  assigned_to?: number;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
}

export interface BugUpdate {
  title?: string;
  description?: string;
  severity?: BugSeverity;
  status?: TaskStatus;
  assigned_to?: number;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  environment?: string;
}

export interface FeedbackCreate {
  category: string;
  title: string;
  description?: string;
  rating?: number;
  project_id: number;
  tags?: string[];
}

export interface FeedbackUpdate {
  category?: string;
  title?: string;
  description?: string;
  rating?: number;
  status?: string;
  tags?: string[];
}

export interface ReleaseCreate {
  version: string;
  title: string;
  description?: string;
  release_notes?: string;
  status?: string;
  project_id: number;
  changes?: Record<string, any>[];
}

export interface ReleaseUpdate {
  version?: string;
  title?: string;
  description?: string;
  release_notes?: string;
  status?: string;
  changes?: Record<string, any>[];
}

export interface CodeReviewCreate {
  project_id: number;
  reviewer_id: number;
  author_id: number;
  pull_request_url?: string;
  title: string;
  description?: string;
  status?: string;
  review_data?: Record<string, any>;
}

export interface CodeReviewUpdate {
  pull_request_url?: string;
  title?: string;
  description?: string;
  status?: string;
  review_data?: Record<string, any>;
} 