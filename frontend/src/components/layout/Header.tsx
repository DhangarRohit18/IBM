import { useState } from 'react'
import { Search, Bell, ChevronDown } from 'lucide-react'
import { Link } from 'react-router-dom'
import { GlobalSearchModal } from '../ui/GlobalSearchModal'

export function Header() {
  const [searchOpen, setSearchOpen] = useState(false)

  return (
    <>
      <header className="h-[60px] bg-white border-b border-slate-200 px-5 flex items-center justify-between gap-4 sticky top-0 z-30 shadow-xs">
        {/* Left Branding */}
        <div className="flex items-center gap-3 min-w-[240px]">
          <Link to="/" className="flex flex-col text-decoration-none group">
            <div className="flex items-center gap-1">
              <span className="font-extrabold text-lg tracking-tight text-slate-900 font-sans">
                LEGACY<span className="text-teal-600">X</span>
              </span>
            </div>
            <span className="text-[10px] font-medium text-slate-500 tracking-tight -mt-1">
              Understand. Modernize. Move Forward.
            </span>
          </Link>
        </div>

        {/* Center Global Search Trigger */}
        <div className="flex-1 max-w-xl">
          <button
            onClick={() => setSearchOpen(true)}
            className="w-full flex items-center justify-between px-3.5 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-500 transition-all cursor-pointer group"
          >
            <div className="flex items-center gap-2.5">
              <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors" />
              <span className="font-normal text-slate-500">Search projects, components, rules, or files...</span>
            </div>
            <kbd className="px-2 py-0.5 text-[10px] font-semibold text-slate-500 bg-white border border-slate-200 rounded shadow-2xs font-mono">
              Ctrl K
            </kbd>
          </button>
        </div>

        {/* Right User & Actions */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button
            className="relative p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full ring-2 ring-white" />
          </button>

          <div className="h-5 w-px bg-slate-200" />

          {/* User Profile Dropdown */}
          <div className="flex items-center gap-2.5 pl-1 cursor-pointer group">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center shadow-xs ring-2 ring-slate-100">
              SK
            </div>
            <div className="flex flex-col text-left hidden sm:flex">
              <span className="text-xs font-bold text-slate-900 group-hover:text-teal-700 transition-colors leading-tight">
                Sarvesh K
              </span>
              <span className="text-[10px] font-medium text-slate-500 leading-tight">
                TerminalX
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors hidden sm:block" />
          </div>
        </div>
      </header>

      {/* Global Search Command Palette Modal */}
      {searchOpen && <GlobalSearchModal onClose={() => setSearchOpen(false)} />}
    </>
  )
}
