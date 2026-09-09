/**
 * LEGACYX — Shared Page Header Banner.
 *
 * Uniform enterprise header banner used across all primary pages.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import type { ReactNode } from 'react'

interface PageHeaderProps {
  /** Small all-caps eyebrow label above the title */
  eyebrow?: ReactNode
  /** Icon element for the eyebrow */
  eyebrowIcon?: ReactNode
  /** Main h1 title */
  title: ReactNode
  /** Subtitle / description */
  subtitle?: string
  /** Optional right-side action slot */
  actions?: ReactNode
}

export function PageHeader({ eyebrow, eyebrowIcon, title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl px-6 py-5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="space-y-1">
        {eyebrow && (
          <div className="flex items-center gap-1.5 text-teal-700 font-extrabold text-[10px] tracking-widest uppercase">
            {eyebrowIcon}
            <span>{eyebrow}</span>
          </div>
        )}
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">{title}</h1>
        {subtitle && (
          <p className="text-xs text-slate-500 leading-relaxed max-w-3xl">{subtitle}</p>
        )}
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </div>
  )
}
