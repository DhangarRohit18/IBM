import { Routes, Route } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { ProjectsPage } from '@/features/projects/ProjectsPage'
import { ProjectWorkspacePage } from '@/features/projects/ProjectWorkspacePage'
import { SettingsPage } from '@/features/settings/SettingsPage'
import { DocumentationPage } from '@/features/documentation/DocumentationPage'
import { NotFoundPage } from '@/components/feedback/NotFoundPage'

export function Router() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="projects/:projectId" element={<ProjectWorkspacePage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="documentation" element={<DocumentationPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
