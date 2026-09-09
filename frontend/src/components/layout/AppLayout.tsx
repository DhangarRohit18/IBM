/**
 * LEGACYX — App Layout Shell.
 *
 * Uses a flex-row layout where the sidebar is a normal flex child (shrink-0)
 * and the main content area expands to fill remaining width (flex-1 min-w-0).
 * This avoids the fragility of fixed positioning + margin-left offsets.
 *
 * Sidebar is sticky (top-0, h-screen) so it scrolls with the viewport edge
 * but stays visually anchored without needing position:fixed on the sidebar.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function AppLayout() {
  return (
    <div className="flex min-h-screen bg-[#ebf1f6] text-slate-900 font-sans">
      {/* ── Sidebar ────────────────────────────────────────────────────────── */}
      {/* shrink-0 prevents the sidebar from ever being compressed by flex layout */}
      <div className="shrink-0 w-[250px]">
        <Sidebar />
      </div>

      {/* ── Main Shell ─────────────────────────────────────────────────────── */}
      {/* min-w-0 allows this column to shrink below its content size,
          preventing flex blowout when child content is wide */}
      <div className="flex-1 min-w-0 flex flex-col min-h-screen">
        {/* Sticky Top Header — contained within this column, not full-viewport */}
        <Header />

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-[1400px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
