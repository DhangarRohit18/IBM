import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function AppLayout() {
  return (
    <div className="min-h-screen bg-[#ebf1f6] text-slate-900 font-sans flex">
      {/* Fixed Sidebar */}
      <Sidebar />

      {/* Main Container Right of Sidebar */}
      <div className="flex-1 ml-[250px] flex flex-col min-w-0 min-h-screen">
        {/* Sticky Top Header */}
        <Header />

        {/* Main Scrollable Content */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          <div className="max-w-[1600px] mx-auto space-y-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
