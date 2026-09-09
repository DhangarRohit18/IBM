/**
 * LEGACYX — Main App Header Bar.
 *
 * Sticky header with dynamic breadcrumbs, command search trigger,
 * system verification badge, and user controls.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { useState } from 'react'
import { Search, Bell, ChevronDown, ChevronRight, Home, ShieldCheck } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { GlobalSearchModal } from '../ui/GlobalSearchModal'

export function Header() {
  const [searchOpen, setSearchOpen] = useState(false)
  const location = useLocation()

  // Generate dynamic breadcrumbs based on URL path
  const pathParts = location.pathname.split('/').filter(Boolean)

  return (
    <>
      <header className="h-[56px] bg-white border-b border-slate-200/80 px-6 flex items-center justify-between gap-4 sticky top-0 z-30 shadow-2xs shrink-0 min-w-0">
        {/* Left: Dynamic Breadcrumbs */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 min-w-0 shrink-0">
          <Link
            to="/"
            className="flex items-center gap-1.5 text-slate-500 hover:text-teal-700 transition-colors no-underline"
          >
            <Home className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Workspace</span>
          </Link>
          {pathParts.length > 0 && <ChevronRight className="w-3.5 h-3.5 text-slate-300 shrink-0" />}
          {pathParts.map((part, index) => {
            const isLast = index === pathParts.length - 1
            const to = '/' + pathParts.slice(0, index + 1).join('/')
            const label = part.charAt(0).toUpperCase() + part.slice(1)
            return (
              <div key={to} className="flex items-center gap-2 min-w-0">
                {isLast ? (
                  <span className="font-extrabold text-slate-900 truncate max-w-[200px]">
                    {label}
                  </span>
                ) : (
                  <Link to={to} className="text-slate-500 hover:text-teal-700 transition-colors truncate max-w-[120px]">
                    {label}
                  </Link>
                )}
                {!isLast && <ChevronRight className="w-3.5 h-3.5 text-slate-300 shrink-0" />}
              </div>
            )
          })}
        </div>

        {/* Center: Global Command Search Palette Button */}
        <div className="flex-1 min-w-0 max-w-md mx-auto hidden md:block">
          <button
            onClick={() => setSearchOpen(true)}
            id="global-search-trigger"
            className="w-full flex items-center justify-between px-3.5 py-1.5 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-lg text-xs text-slate-500 transition-all cursor-pointer group shadow-2xs"
          >
            <div className="flex items-center gap-2 min-w-0">
              <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-teal-600 transition-colors shrink-0" />
              <span className="font-normal text-slate-400 truncate">Search repositories, rules, AST components...</span>
            </div>
            <kbd className="ml-2 px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 bg-white border border-slate-200 rounded font-mono shrink-0">
              Ctrl K
            </kbd>
          </button>
        </div>

        {/* Right: User Controls & Status */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold">
            <ShieldCheck className="w-3 h-3 text-emerald-600" />
            <span>Deterministic Verified</span>
          </div>

          <button
            onClick={() => setSearchOpen(true)}
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer md:hidden"
            title="Search"
          >
            <Search className="w-4 h-4" />
          </button>

          <button
            className="relative p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            title="Notifications"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full ring-2 ring-white" />
          </button>

          <div className="h-4 w-px bg-slate-200" />

          {/* Profile Dropdown */}
          <div className="flex items-center gap-2 cursor-pointer group">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-slate-800 to-slate-950 text-white font-bold text-xs flex items-center justify-center shadow-2xs ring-2 ring-slate-100 shrink-0">
              SK
            </div>
            <div className="flex-col text-left hidden sm:flex">
              <span className="text-xs font-bold text-slate-800 group-hover:text-teal-700 transition-colors leading-tight">
                Sarvesh K
              </span>
              <span className="text-[10px] text-slate-400 leading-tight font-mono">
                Lead Auditor
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors hidden sm:block" />
          </div>
        </div>
      </header>

      {/* Global Search Modal */}
      {searchOpen && <GlobalSearchModal onClose={() => setSearchOpen(false)} />}
    </>
  )
}
