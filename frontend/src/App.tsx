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
import ForgotPasswordPageNew from "@/components/ForgotPasswordPageNew";
import ComponentDemo from "@/components/ComponentDemo";
import ResetPasswordPageNew from "@/components/ResetPasswordPageNew";
import DashboardHomeNew from "@/components/DashboardHomeNew";
import OrganizationPage from "@/components/OrganizationPage";
import UserManagementPage from "@/components/UserManagementPage";
import UserApprovalPage from "@/components/UserApprovalPage";
import RoleManagementPage from "@/components/RoleManagementPage";
import InvitationManagementPage from "@/components/InvitationManagementPage";
import DeveloperAdminPanelNew from "@/components/DeveloperAdminPanelNew";
import SettingsPage from "@/components/EnhancedSettingsPageNew";
import MFASetupPageNew from "@/components/MFASetupPageNew";
import InspectionsPageNew from "@/components/InspectionsPageNew";
import TemplateBuilderPageNew from "@/components/TemplateBuilderPageNew";
import InspectionExecutionPageNew from "@/components/InspectionExecutionPageNew";
import ChecklistsPageNew from "@/components/ChecklistsPageNew";
import ChecklistTemplateBuilderNew from "@/components/ChecklistTemplateBuilderNew";
import ChecklistExecutionPageNew from "@/components/ChecklistExecutionPageNew";
import TasksPageNew from "@/components/TasksPageNew";
import ReportsPageNew from "@/components/ReportsPageNew";
import WorkflowDesignerNew from "@/components/WorkflowDesignerNew";
import MyApprovalsPageNew from "@/components/MyApprovalsPageNew";
import DelegationManagerNew from "@/components/DelegationManagerNew";
import AuditViewerNew from "@/components/AuditViewerNew";
import AnalyticsDashboardNew from "@/components/AnalyticsDashboardNew";
import GroupsManagementPageNew from "@/components/GroupsManagementPageNew";
import BulkImportPageNew from "@/components/BulkImportPageNew";
import WebhooksPageNew from "@/components/WebhooksPageNew";
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
                    <OrganizationPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InspectionsPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/new"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <TemplateBuilderPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/:templateId/edit"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <TemplateBuilderPageNew />
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
                    <UserManagementPageNew />
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
                    <RoleManagementPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/invitations"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <InvitationManagementPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <ChecklistsPageNew />
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
                    <TasksPageNew />
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
                    <ReportsPageNew />
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
                    <MyApprovalsPageNew />
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
                    <GroupsManagementPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/bulk-import"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <BulkImportPageNew />
                  </LayoutNew>
                </ProtectedRoute>
              }
            />
            <Route
              path="/webhooks"
              element={
                <ProtectedRoute>
                  <LayoutNew>
                    <WebhooksPageNew />
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
