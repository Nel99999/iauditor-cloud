import React from "react";
import "@/App.css";
// Import Design System tokens FIRST
import "@/design-system/tokens/base.css";
// Import global modern overrides to modernize ALL existing components
import "@/design-system/global-modern-overrides.css";
import InspectionExecutionPage from "@/components/InspectionExecutionPage";
import EnhancedInspectionExecutionPage from "@/components/EnhancedInspectionExecutionPage";
import ChecklistsPage from "@/components/ChecklistsPage";

import AnnouncementsPage from "@/components/AnnouncementsPage";
import EmergenciesPage from "@/components/EmergenciesPage";
import TeamChatPage from "@/components/TeamChatPage";
import ContractorsPage from "@/components/ContractorsPage";
import HRPage from "@/components/HRPage";
import WorkOrderDetailPage from "@/components/WorkOrderDetailPage";
import ProjectDetailPage from "@/components/ProjectDetailPage";
import InventoryDetailPage from "@/components/InventoryDetailPage";
import IncidentDetailPage from "@/components/IncidentDetailPage";
import WorkOrderFormPage from "@/components/WorkOrderFormPage";
import ProjectFormPage from "@/components/ProjectFormPage";
import ThemeShowcase from "@/components/ThemeShowcase";
import InspectionCalendar from "@/components/InspectionCalendar";

// Placeholder components for future features


function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <ThemeProvider>
            <RouteMiddleware>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/component-demo" element={<ComponentDemo />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

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
                        <DashboardHome />
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
                        <EnhancedTemplateBuilderPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/inspections/templates/:templateId/edit"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <EnhancedTemplateBuilderPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/inspections/execute/:templateId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <EnhancedInspectionExecutionPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/inspections/executions/:executionId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <InspectionExecutionPage />
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
                        <UserManagementPage />
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
                        <EnhancedChecklistBuilderPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/checklists/templates/:templateId/edit"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <EnhancedChecklistBuilderPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/checklists/execute/:executionId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ChecklistExecutionPage />
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
                  path="/assets"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AssetsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assets/new"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AssetFormPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assets/:assetId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AssetDetailPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assets/:assetId/edit"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AssetFormPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/work-orders"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <WorkOrdersPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/work-orders/new"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <WorkOrderFormPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/work-orders/:woId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <WorkOrderDetailPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/inventory"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <InventoryPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/inventory/:itemId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <InventoryDetailPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ProjectsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/new"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ProjectFormPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ProjectDetailPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/incidents"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <IncidentsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/incidents/:incidentId"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <IncidentDetailPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/chat"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <TeamChatPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/contractors"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ContractorsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/training"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <TrainingPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboards"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <DashboardsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/financial"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <FinancialPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/announcements"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AnnouncementsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/emergencies"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <EmergenciesPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/schedule"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <InspectionCalendar />
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
                {/* Documents route removed until implementation */}
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ModernSettingsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/workflows"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <WorkflowDesigner />
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
                        <DelegationManager />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/audit"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AuditViewer />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <AnalyticsDashboard />
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
                        <MFASetupPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <ModernSettingsPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/developer-admin"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <DeveloperAdminPanel />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/team-chat"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <TeamChatPage />
                      </LayoutNew>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/hr"
                  element={
                    <ProtectedRoute>
                      <LayoutNew>
                        <HRPage />
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
