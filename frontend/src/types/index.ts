/**
 * Global Type Definitions for v2.0 Operational Management Platform
 */

// ==================== User Types ====================

export type UserRole =
  | 'master'
  | 'admin'
  | 'developer'
  | 'operations_manager'
  | 'team_lead'
  | 'manager'
  | 'supervisor'
  | 'inspector'
  | 'operator'
  | 'viewer';

export type UserStatus = 'active' | 'inactive' | 'suspended' | 'deleted';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  role_name?: string;
  status: UserStatus;
  organization_id?: string;
  created_at: string;
  last_login?: string;
  phone?: string;
  bio?: string;
  profile_picture?: string;
  permissions?: string[];
}

export interface UserProfile extends User {
  settings?: UserSettings;
  preferences?: UserPreferences;
}

export interface UserSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  weekly_reports: boolean;
  marketing_emails: boolean;
}

export interface UserPreferences {
  theme?: 'light' | 'dark';
  accent_color?: string;
  density?: 'compact' | 'comfortable' | 'spacious';
  font_size?: 'small' | 'medium' | 'large';
  language?: string;
  timezone?: string;
  date_format?: string;
  time_format?: '12h' | '24h';
  currency?: string;
}

// ==================== Task Types ====================

export type TaskStatus = 'todo' | 'in-progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assigned_to?: string;
  assigned_to_name?: string;
  created_by: string;
  organization_id: string;
  due_date?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
  comments?: TaskComment[];
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  user_name: string;
  comment: string;
  created_at: string;
}

export interface Subtask {
  id: string;
  parent_task_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  assigned_to?: string;
  due_date?: string;
  created_at: string;
}

export interface TaskStats {
  total: number;
  todo: number;
  in_progress: number;
  completed: number;
  overdue: number;
}

// ==================== Inspection Types ====================

export type InspectionStatus = 'pending' | 'in-progress' | 'completed';
export type QuestionType = 'yes_no' | 'number' | 'text' | 'multiple_choice' | 'photo';

export interface InspectionQuestion {
  question: string;
  type: QuestionType;
  required: boolean;
  options?: string[];
}

export interface InspectionTemplate {
  id: string;
  name: string;
  description?: string;
  questions: InspectionQuestion[];
  organization_id: string;
  created_by: string;
  created_at: string;
  is_active: boolean;
}

export interface InspectionAnswer {
  question: string;
  answer: string | number | boolean;
  photo_id?: string;
}

export interface Inspection {
  id: string;
  template_id: string;
  template_name: string;
  inspector_id: string;
  inspector_name: string;
  status: InspectionStatus;
  answers: InspectionAnswer[];
  score?: number;
  pass_rate?: number;
  organization_id: string;
  started_at: string;
  completed_at?: string;
}

export interface InspectionStats {
  total_inspections: number;
  pending: number;
  completed_today: number;
  pass_rate: number;
  average_score: number | null;
}

// ==================== Checklist Types ====================

export type ChecklistStatus = 'not_started' | 'in_progress' | 'completed';

export interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
}

export interface ChecklistTemplate {
  id: string;
  name: string;
  description?: string;
  items: string[];
  organization_id: string;
  created_by: string;
  created_at: string;
  is_active: boolean;
}

export interface ChecklistExecution {
  id: string;
  template_id: string;
  template_name: string;
  items: ChecklistItem[];
  status: ChecklistStatus;
  assignee_id: string;
  assignee_name: string;
  organization_id: string;
  started_at: string;
  completed_at?: string;
  completion_percentage: number;
}

export interface ChecklistStats {
  total_checklists: number;
  completed_today: number;
  pending_today: number;
  completion_rate: number;
}

// ==================== Organization Types ====================

export type OrgLevel = 'company' | 'region' | 'location' | 'department' | 'team';

export interface OrganizationUnit {
  id: string;
  name: string;
  level: number;
  level_name: OrgLevel;
  parent_id?: string;
  organization_id: string;
  created_at: string;
  children?: OrganizationUnit[];
}

export interface Organization {
  id: string;
  name: string;
  created_at: string;
  created_by: string;
}

export interface OrganizationStats {
  total_units: number;
  total_levels: number;
}

// ==================== Workflow Types ====================

export type WorkflowStatus = 'pending' | 'approved' | 'rejected';
export type WorkflowNodeType = 'start' | 'approval' | 'end' | 'condition';

export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  label: string;
  approver_role?: string;
  conditions?: Record<string, any>;
}

export interface WorkflowEdge {
  source: string;
  target: string;
  condition?: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  organization_id: string;
  created_by: string;
  created_at: string;
  is_active: boolean;
}

export interface WorkflowInstance {
  id: string;
  template_id: string;
  template_name: string;
  initiator_id: string;
  initiator_name: string;
  current_node: string;
  status: WorkflowStatus;
  data: Record<string, any>;
  organization_id: string;
  created_at: string;
  completed_at?: string;
}

// ==================== Permission Types ====================

export interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  module?: string;
  is_system: boolean;
}

export interface Role {
  id: string;
  name: string;
  code: string;
  level: number;
  color: string;
  description?: string;
  is_system: boolean;
  permissions: string[];
}

// ==================== Dashboard Types ====================

export interface UserStats {
  total_users: number;
  active_users: number;
  pending_invitations: number;
  recent_logins: number;
}

export interface DashboardStats {
  users: UserStats;
  inspections: InspectionStats;
  tasks: TaskStats;
  checklists: ChecklistStats;
  organization: OrganizationStats;
}

// ==================== API Types ====================

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  message: string;
  detail?: string;
  status_code: number;
}

// ==================== Form Types ====================

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  organization_name?: string;
}

export interface TaskFormData {
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  due_date?: string;
  assigned_to?: string;
  tags?: string[];
}

export interface InvitationFormData {
  email: string;
  role: UserRole;
  organization_unit_id?: string;
}

// ==================== Context Types ====================

export interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterFormData) => Promise<void>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

// ==================== Component Prop Types ====================

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  children?: React.ReactNode;
  className?: string;
}

export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps {
  padding?: CardPadding;
  className?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
  onClick?: () => void;
  hover?: boolean;
}

export type GlassCardBlur = 'sm' | 'md' | 'lg' | 'xl';

export interface GlassCardProps extends CardProps {
  hover?: boolean;
  blur?: GlassCardBlur;
}

export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: InputSize;
  icon?: React.ReactNode;
  error?: boolean;
}

export type BottomSheetSnapPoint = 'peek' | 'half' | 'full';

export interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  snapPoint?: BottomSheetSnapPoint;
  title?: string;
  showDragHandle?: boolean;
  enableSwipe?: boolean;
  children: React.ReactNode;
  className?: string;
}

export type FABVariant = 'simple' | 'speedDial';
export type FABPosition = 'bottom-right' | 'bottom-center' | 'bottom-left';
export type FABColor = 'primary' | 'secondary' | 'success' | 'danger';
export type FABSize = 'default' | 'large';

export interface FABAction {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  color?: FABColor | 'warning' | 'info';
}

export interface FABProps {
  variant?: FABVariant;
  position?: FABPosition;
  icon: React.ReactNode;
  label?: string;
  color?: FABColor;
  size?: FABSize;
  onClick?: () => void;
  actions?: FABAction[];
  className?: string;
}

// ==================== Report Types ====================

export interface ReportFilter {
  start_date?: string;
  end_date?: string;
  status?: string;
  user_id?: string;
  organization_unit_id?: string;
}

export interface Report {
  id: string;
  name: string;
  type: string;
  filters: ReportFilter;
  created_by: string;
  created_at: string;
  data?: any;
}

export interface AnalyticsData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

// ==================== Notification Types ====================

export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'task' | 'inspection';

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  link?: string;
  read: boolean;
  created_at: string;
}

// ==================== Time Tracking Types ====================

export interface TimeEntry {
  id: string;
  user_id: string;
  task_id: string;
  task_title: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  description?: string;
  created_at: string;
}

// ==================== Webhook Types ====================

export interface Webhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  is_active: boolean;
  secret?: string;
  organization_id: string;
  created_at: string;
}

// ==================== Group Types ====================

export interface Group {
  id: string;
  name: string;
  description?: string;
  member_ids: string[];
  organization_id: string;
  created_by: string;
  created_at: string;
}

// ==================== Mention Types ====================

export interface Mention {
  id: string;
  user_id: string;
  user_name: string;
  entity_type: 'task' | 'comment' | 'inspection';
  entity_id: string;
  created_at: string;
}

// ==================== Search Types ====================

export interface SearchResult {
  type: 'task' | 'user' | 'inspection' | 'checklist' | 'group';
  id: string;
  title: string;
  subtitle?: string;
  icon?: string;
  link: string;
}

export interface GlobalSearchResponse {
  results: SearchResult[];
  total: number;
}


// ==================== Delegation Types ====================

export interface Delegation {
  id: string;
  delegator_id: string;
  delegator_name: string;
  delegate_id: string;
  delegate_name: string;
  reason?: string;
  valid_from: string;
  valid_until: string;
  workflow_types?: string[];
  resource_types?: string[];
  is_active: boolean;
  organization_id: string;
  created_at: string;
}

// ==================== Audit Types ====================

export interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_name: string;
  action: string;
  resource_type: string;
  resource_id: string;
  result: 'success' | 'failure';
  permission_checked?: string;
  changes?: Record<string, any>;
  organization_id: string;
}

export interface AuditStats {
  total_logs: number;
  failed_permissions: number;
  top_users: Array<{ user_name: string; count: number }>;
  actions: Record<string, number>;
}

export interface AuditFilters {
  action: string;
  resource_type: string;
  result: string;
  start_date: string;
  end_date: string;
  limit: number;
  [key: string]: string | number;
}

// ==================== Analytics Types ====================

export interface AnalyticsOverview {
  metrics: {
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    total_time_tracked: number;
    active_users: number;
    total_inspections: number;
  };
}

export interface TaskTrendData {
  name: string;
  value: number;
}

export interface TaskStatusData {
  name: string;
  count: number;
}

export interface UserActivityData {
  user_name: string;
  tasks_completed: number;
  hours_logged: number;
  last_activity: string;
}

// ==================== Bulk Import Types ====================

export interface BulkImportValidation {
  total_count: number;
  valid_count: number;
  invalid_count: number;
  is_valid: boolean;
  errors?: Array<{ row: number; message: string }>;
  preview?: Array<Record<string, any>>;
}

export interface BulkImportResult {
  success_count: number;
  failed_count: number;
  failed_users?: Array<{ row: number; error: string }>;
}

// ==================== Settings Types ====================

export interface EmailSettings {
  sendgrid_api_key?: string;
  from_email?: string;
  from_name?: string;
}

export interface SMSSettings {
  twilio_account_sid?: string;
  twilio_auth_token?: string;
  twilio_phone_number?: string;
}

export interface SecurityPreferences {
  two_factor_enabled: boolean;
  session_timeout: number;
  ip_whitelist?: string[];
}

export interface RegionalPreferences {
  language: string;
  timezone: string;
  date_format: string;
  time_format: '12h' | '24h';
  currency: string;
}

export interface PrivacyPreferences {
  profile_visibility: 'public' | 'private' | 'team';
  show_activity: boolean;
  show_last_seen: boolean;
}

// ==================== Invitation Types ====================

export interface Invitation {
  id: string;
  email: string;
  role: UserRole;
  status: 'pending' | 'accepted' | 'expired' | 'cancelled';
  organization_id: string;
  sent_by: string;
  sent_by_name?: string;
  sent_at: string;
  expires_at: string;
  accepted_at?: string;
  token?: string;
}

// ==================== MFA Types ====================

export interface MFASetup {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

export interface MFAVerification {
  code: string;
  backup_code?: boolean;
}

// ==================== Workflow Designer Types ====================

export interface FlowNode {
  id: string;
  type: 'start' | 'approval' | 'condition' | 'action' | 'end';
  data: {
    label: string;
    approver_role?: string;
    conditions?: Record<string, any>;
    actions?: string[];
  };
  position: { x: number; y: number };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
}

// ==================== Role Management Types ====================

export interface RoleFormData {
  name: string;
  code: string;
  level: number;
  color: string;
  description?: string;
  permissions: string[];
}

export interface PermissionGroup {
  module: string;
  permissions: Permission[];
}

// ==================== Developer Panel Types ====================

export interface SystemInfo {
  version: string;
  environment: string;
  database_status: string;
  cache_status: string;
  api_status: string;
}

export interface RoleMapping {
  [key: string]: string;
}

export interface PermissionOverride {
  user_id: string;
  permission_id: string;
  granted: boolean;
  reason?: string;
  created_at: string;
}
