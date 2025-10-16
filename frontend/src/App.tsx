import React from "react";
import "@/App.css";
// Import Design System tokens FIRST
import "@/design-system/tokens/base.css";
// Import global modern overrides to modernize ALL existing components
import "@/design-system/global-modern-overrides.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import "@/i18n/config";
import RouteMiddleware from "@/routing/RouteMiddleware";
import ProtectedRoute from "@/components/ProtectedRoute";
import LayoutNew from "@/components/LayoutNew";
import LoginPage from "@/components/LoginPage";
import LoginPageNew from "@/components/LoginPageNew";
import RegisterPage from "@/components/RegisterPage";
import RegisterPageNew from "@/components/RegisterPageNew";
import ForgotPasswordPage from "@/components/ForgotPasswordPage";
import ComponentDemo from "@/components/ComponentDemo";
import ResetPasswordPage from "@/components/ResetPasswordPage";
import DashboardHomeNew from "@/components/DashboardHomeNew";
// Refactored pages - removed wrapper pattern
import OrganizationPage from "@/components/OrganizationPage";
import UserManagementPage from "@/components/UserManagementPage";
import UserApprovalPage from "@/components/UserApprovalPage";
import RoleManagementPage from "@/components/RoleManagementPage";
import InvitationManagementPage from "@/components/InvitationManagementPage";
import DeveloperAdminPanelNew from "@/components/DeveloperAdminPanelNew";
import EnhancedSettingsPage from "@/components/EnhancedSettingsPage";
import MFASetupPage from "@/components/MFASetupPage";
import InspectionsPage from "@/components/InspectionsPage";
import TemplateBuilderPage from "@/components/TemplateBuilderPage";
import InspectionExecutionPage from "@/components/InspectionExecutionPage";
import ChecklistsPage from "@/components/ChecklistsPage";
import ChecklistTemplateBuilderNew from "@/components/ChecklistTemplateBuilderNew";
import ChecklistExecutionPage from "@/components/ChecklistExecutionPage";
import TasksPage from "@/components/TasksPage";
import ReportsPage from "@/components/ReportsPage";
import WorkflowDesignerNew from "@/components/WorkflowDesignerNew";
import MyApprovalsPage from "@/components/MyApprovalsPage";
import DelegationManagerNew from "@/components/DelegationManagerNew";
import AuditViewerNew from "@/components/AuditViewerNew";
import AnalyticsDashboardNew from "@/components/AnalyticsDashboardNew";
import GroupsManagementPage from "@/components/GroupsManagementPage";
import BulkImportPage from "@/components/BulkImportPage";
import WebhooksPage from "@/components/WebhooksPage";
import DesignSystemShowcase from "@/components/DesignSystemShowcase";
import VisualPolishShowcase from "@/components/VisualPolishShowcase";
import ThemeShowcase from "@/components/ThemeShowcase";

// Placeholder components for future features
interface ComingSoonProps {
  feature: string;
}

const ComingSoon: React.FC<ComingSoonProps> = ({ feature }) => (
  <div className="flex items-center justify-center h-96">
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-2">{feature}</h2>
      <p className="text-slate-600">Coming soon in a future milestone!</p>
    </div>
  </div>
);

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <ThemeProvider>
          <RouteMiddleware>
          <Routes>
            <Route path="/login" element={<LoginPageNew />} />
            <Route path="/login-old" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPageNew />} />
            <Route path="/demo" element={<ComponentDemo />} />
            <Route path="/register-old" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPageNew />} />
            <Route path="/reset-password" element={<ResetPasswordPageNew />} />
            
            {/* Design System Showcase - Public route for testing */}
            <Route path="/design-system" element={<DesignSystemShowcase />} />
            <Route path="/visual-polish" element={<VisualPolishShowcase />} />
            <Route path="/theme" element={<ThemeShowcase />} />
            
            {/* Protected routes with Layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <DashboardHomeNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/organization"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <OrganizationPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InspectionsPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/new"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <TemplateBuilderPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/:templateId/edit"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <TemplateBuilderPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/execute/:templateId"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InspectionExecutionPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/executions/:executionId"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InspectionExecutionPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <UserManagementPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users/approvals"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <UserApprovalPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/roles"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <RoleManagementPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/invitations"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InvitationManagementPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ChecklistsPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/templates/new"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ChecklistTemplateBuilderNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/templates/:templateId/edit"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ChecklistTemplateBuilderNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/execute/:executionId"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ChecklistExecutionPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tasks"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <TasksPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/schedule"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ComingSoon feature="Schedule" />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ReportsPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            {/* Removed duplicate /analytics route - using AnalyticsDashboard below */}
            <Route
              path="/documents"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ComingSoon feature="Documents" />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ComingSoon feature="Profile" />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/workflows"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <WorkflowDesignerNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/approvals"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <MyApprovalsPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/delegations"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <DelegationManagerNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <AuditViewerNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <AnalyticsDashboardNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/groups"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <GroupsManagementPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/bulk-import"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <BulkImportPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/webhooks"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <WebhooksPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/security/mfa"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <MFASetupPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <SettingsPage />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/developer-admin"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <DeveloperAdminPanelNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          </RouteMiddleware>
          </ThemeProvider>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
