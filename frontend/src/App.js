import React from "react";
import "@/App.css";
// Import Design System tokens FIRST
import "@/design-system/tokens/base.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import "@/i18n/config";
import RouteMiddleware from "@/routing/RouteMiddleware";
import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";
import LoginPage from "@/components/LoginPage";
import RegisterPage from "@/components/RegisterPage";
import ForgotPasswordPage from "@/components/ForgotPasswordPage";
import ResetPasswordPage from "@/components/ResetPasswordPage";
import DashboardHome from "@/components/DashboardHome";
import OrganizationPage from "@/components/OrganizationPage";
import UserManagementPage from "@/components/UserManagementPage";
import RoleManagementPage from "@/components/RoleManagementPage";
import InvitationManagementPage from "@/components/InvitationManagementPage";
import DeveloperAdminPanel from "@/components/DeveloperAdminPanel";
import SettingsPage from "@/components/EnhancedSettingsPage";
import MFASetupPage from "@/components/MFASetupPage";
import InspectionsPage from "@/components/InspectionsPage";
import TemplateBuilderPage from "@/components/TemplateBuilderPage";
import InspectionExecutionPage from "@/components/InspectionExecutionPage";
import ChecklistsPage from "@/components/ChecklistsPage";
import ChecklistTemplateBuilder from "@/components/ChecklistTemplateBuilder";
import ChecklistExecutionPage from "@/components/ChecklistExecutionPage";
import TasksPage from "@/components/TasksPage";
import ReportsPage from "@/components/ReportsPage";
import WorkflowDesigner from "@/components/WorkflowDesigner";
import MyApprovalsPage from "@/components/MyApprovalsPage";
import DelegationManager from "@/components/DelegationManager";
import AuditViewer from "@/components/AuditViewer";
import AnalyticsDashboard from "@/components/AnalyticsDashboard";
import GroupsManagementPage from "@/components/GroupsManagementPage";
import BulkImportPage from "@/components/BulkImportPage";
import WebhooksPage from "@/components/WebhooksPage";
import DesignSystemShowcase from "@/components/DesignSystemShowcase";

// Placeholder components for future features
const ComingSoon = ({ feature }) => (
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
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            
            {/* Design System Showcase - Public route for testing */}
            <Route path="/design-system" element={<DesignSystemShowcase />} />
            
            {/* Protected routes with Layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DashboardHome />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/organization"
              element={
                <ProtectedRoute>
                  <Layout>
                    <OrganizationPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections"
              element={
                <ProtectedRoute>
                  <Layout>
                    <InspectionsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/new"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TemplateBuilderPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/templates/:templateId/edit"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TemplateBuilderPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/execute/:templateId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <InspectionExecutionPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inspections/executions/:executionId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <InspectionExecutionPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <Layout>
                    <UserManagementPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/roles"
              element={
                <ProtectedRoute>
                  <Layout>
                    <RoleManagementPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/invitations"
              element={
                <ProtectedRoute>
                  <Layout>
                    <InvitationManagementPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChecklistsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/templates/new"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChecklistTemplateBuilder />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/templates/:templateId/edit"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChecklistTemplateBuilder />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/checklists/execute/:executionId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChecklistExecutionPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tasks"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TasksPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/schedule"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ComingSoon feature="Schedule" />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ReportsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            {/* Removed duplicate /analytics route - using AnalyticsDashboard below */}
            <Route
              path="/documents"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ComingSoon feature="Documents" />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ComingSoon feature="Profile" />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/workflows"
              element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowDesigner />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/approvals"
              element={
                <ProtectedRoute>
                  <Layout>
                    <MyApprovalsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/delegations"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DelegationManager />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AuditViewer />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AnalyticsDashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/groups"
              element={
                <ProtectedRoute>
                  <Layout>
                    <GroupsManagementPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/bulk-import"
              element={
                <ProtectedRoute>
                  <Layout>
                    <BulkImportPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/webhooks"
              element={
                <ProtectedRoute>
                  <Layout>
                    <WebhooksPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/security/mfa"
              element={
                <ProtectedRoute>
                  <Layout>
                    <MFASetupPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Layout>
                    <SettingsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/developer-admin"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DeveloperAdminPanel />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          </ThemeProvider>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
