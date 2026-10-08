/**
 * ClaimGraph AI — Application Router.
 *
 * Full application routing with AuthProvider, LoginPage, and ProtectedRoute guards.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import DashboardLayout from '@/layouts/DashboardLayout';
import DashboardPage from '@/pages/DashboardPage';
import LoginPage from '@/pages/LoginPage';
import PlaceholderPage from '@/pages/PlaceholderPage';
import { ClaimsPage } from '@/pages/ClaimsPage';
import { ClaimDetailsPage } from '@/pages/ClaimDetailsPage';
import { FraudMetricsPage } from '@/pages/FraudMetricsPage';
import { InvestigationPage } from '@/pages/InvestigationPage';
import { KnowledgeGraphPage } from '@/pages/KnowledgeGraphPage';
import { PolicyIntelligencePage } from '@/pages/PolicyIntelligencePage';
import { AuditLogsPage } from '@/pages/AuditLogsPage';
import { AIEvaluationPage } from '@/pages/AIEvaluationPage';
import { ModelMonitoringPage } from '@/pages/ModelMonitoringPage';


export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
          {/* Public Authentication Route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Authenticated Workspace Routes */}
          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />

            {/* Claims Management — Real Backend Connected */}
            <Route path="claims" element={<ClaimsPage />} />
            <Route path="claims/:id" element={<ClaimDetailsPage />} />

            {/* Fraud Intelligence & Real ML Benchmarks */}
            <Route path="fraud" element={<FraudMetricsPage />} />

            {/* Intelligence Services — Phase 4 Core AI Engine */}
            <Route path="investigation" element={<InvestigationPage />} />
            <Route path="graph" element={<KnowledgeGraphPage />} />
            <Route path="policy" element={<PolicyIntelligencePage />} />

            <Route
              path="documents"
              element={
                <PlaceholderPage
                  title="Document Management"
                  description="Upload, view, and analyze claim-related documents and images."
                  phase="Phase 3"
                  features={[
                    'Document upload',
                    'PDF viewer',
                    'Image analysis',
                    'OCR extraction',
                  ]}
                />
              }
            />

            {/* Operations */}
            <Route
              path="analytics"
              element={
                <PlaceholderPage
                  title="Analytics"
                  description="Claims analytics, trends, and operational metrics."
                  phase="Phase 4+"
                  features={[
                    'Claims volume trends',
                    'Fraud rate analysis',
                    'Processing time metrics',
                    'Geographic distribution',
                  ]}
                />
              }
            />
            <Route
              path="model-performance"
              element={
                <PlaceholderPage
                  title="Model Performance"
                  description="ML model metrics, versioning, and A/B comparison."
                  phase="Phase 6"
                  features={[
                    'Precision/Recall/F1',
                    'ROC-AUC curves',
                    'Model versioning',
                    'MLflow integration',
                  ]}
                />
              }
            />
            <Route path="ai-evaluation" element={<AIEvaluationPage />} />
            <Route path="drift" element={<ModelMonitoringPage />} />
            <Route path="model-performance" element={<ModelMonitoringPage />} />

            {/* Admin & Security — Protected with Role Authorization */}
            <Route
              path="audit"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'INVESTIGATOR']}>
                  <AuditLogsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="users"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'INVESTIGATOR', 'ANALYST']}>
                  <PlaceholderPage
                    title="User Management"
                    description="User accounts, roles, and permission management."
                    phase="Phase 2 (Active Foundation)"
                    features={[
                      'Role assignment (ADMIN/INVESTIGATOR/ANALYST/CUSTOMER)',
                      'Organization tenants',
                      'Profile links (Customer / Investigator)',
                      'Account status control',
                    ]}
                  />
                </ProtectedRoute>
              }
            />
            <Route
              path="settings"
              element={
                <PlaceholderPage
                  title="Settings"
                  description="System configuration and platform preferences."
                  phase="Phase 2+"
                  features={[
                    'System configuration',
                    'Notification preferences',
                    'API key management',
                    'Theme settings',
                  ]}
                />
              }
            />
          </Route>

          {/* Catch-all redirect to Dashboard / Login */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </ThemeProvider>
  </BrowserRouter>
  );
}
