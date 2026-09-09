/**
 * LEGACYX — Settings & Health Page.
 *
 * Infrastructure health monitoring, security storage policy limits,
 * and architectural governance principles.
 *
 * Layer: Presentation (AGENTS.md §1.3)
 */

import { useState, useEffect } from 'react'
import {
  Settings,
  Server,
  Database,
  Cpu,
  Shield,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Lock,
  Layers,
  Activity,
} from 'lucide-react'
import { api, type HealthResponse, type HealthStatusItem } from '@/services/api'
import { PageHeader } from '@/components/ui/PageHeader'

interface ServiceCardProps {
  icon: React.ReactNode
  iconBg: string
  label: string
  name: string
  status: string
  detail: string
}

function ServiceCard({ icon, iconBg, label, name, status, detail }: ServiceCardProps) {
  const ok = status.toLowerCase() === 'ok' || status.toLowerCase() === 'healthy'
  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 flex flex-col gap-3 shadow-2xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className={`w-8 h-8 rounded-xl ${iconBg} border border-slate-100 flex items-center justify-center shrink-0`}>
            {icon}
          </div>
          <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">{label}</span>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide border ${
          ok
            ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
            : 'bg-rose-50 text-rose-700 border-rose-300'
        }`}>
          {ok ? 'Healthy' : status}
        </span>
      </div>
      <div>
        <div className="text-base font-black text-slate-900">{name}</div>
        <div className="text-[11px] font-mono text-slate-500 mt-0.5">{detail}</div>
      </div>
      <div className={`h-1 w-full rounded-full ${ok ? 'bg-emerald-500' : 'bg-rose-500'}`} />
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  subtext: string
}

function StatCard({ label, value, subtext }: StatCardProps) {
  return (
    <div className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 shadow-2xs space-y-1">
      <div className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">{label}</div>
      <div className="text-xl font-black text-slate-900">{value}</div>
      <div className="text-[10px] text-slate-400 font-medium">{subtext}</div>
    </div>
  )
}

export function SettingsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.get<HealthResponse>('/health')
      setHealth(data)
    } catch {
      setError('Unable to fetch backend service status. Ensure backend container is running.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchHealth() }, [])

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <PageHeader
        eyebrowIcon={<Settings className="w-3.5 h-3.5" />}
        eyebrow="Platform Governance & Infrastructure Settings"
        title="System Configuration & Health"
        subtitle="Inspect platform health, backend services, security storage limits, and environment settings."
        actions={
          <button
            onClick={fetchHealth}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer shadow-2xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            Refresh Status
          </button>
        }
      />

      {/* Backend Infrastructure Health */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs space-y-5">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">Backend Infrastructure Health</h2>
              <p className="text-xs text-slate-500">Live operational status of microservices and persistence layers</p>
            </div>
          </div>
          {health && !error && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-300">
              <CheckCircle2 className="w-3.5 h-3.5" /> SYSTEM NOMINAL
            </span>
          )}
        </div>

        {error ? (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : loading ? (
          <div className="py-8 text-center text-xs text-slate-400">
            Querying backend service health...
          </div>
        ) : health ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ServiceCard
              icon={<Server className="w-4 h-4 text-blue-600" />}
              iconBg="bg-blue-50"
              label="FASTAPI APP"
              name={`${health.app_name} v${health.app_version}`}
              status={health.status}
              detail={`Environment: ${health.environment}`}
            />
            {health.services.map((svc: HealthStatusItem) => {
              const isPostgres = svc.name.toLowerCase().includes('postgres')
              return (
                <ServiceCard
                  key={svc.name}
                  icon={isPostgres
                    ? <Database className="w-4 h-4 text-emerald-600" />
                    : <Cpu className="w-4 h-4 text-amber-600" />
                  }
                  iconBg={isPostgres ? 'bg-emerald-50' : 'bg-amber-50'}
                  label={svc.name.toUpperCase()}
                  name={`${svc.name.charAt(0).toUpperCase() + svc.name.slice(1)} Service`}
                  status={svc.status}
                  detail="Connected & Verified"
                />
              )
            })}
          </div>
        ) : null}
      </div>

      {/* Storage & Security Limits */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Storage & Security Policy Limits</h2>
            <p className="text-xs text-slate-500">Enforced repository upload and extraction boundaries</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="MAX UPLOAD SIZE"    value="50 MB"         subtext="ZIP archive upload limit" />
          <StatCard label="MAX EXTRACTED SIZE" value="250 MB"        subtext="Extracted source boundary" />
          <StatCard label="MAX FILE COUNT"     value="10,000 Files"  subtext="Zip Slip protection limit" />
          <StatCard label="STORAGE PATH"       value="/app/storage"  subtext="Immutable source storage" />
        </div>
      </div>

      {/* Governance & Architectural Principles */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-2xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Architectural Governance Principles</h2>
            <p className="text-xs text-slate-500">Core system guarantees enforced by AGENTS.md rules</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              icon: <CheckCircle2 className="w-4 h-4 text-teal-600" />,
              bg: 'bg-teal-50',
              title: 'Deterministic First',
              body: 'All repository facts (files, classes, AST relationships, call sites) are parsed deterministically without AI inference.',
            },
            {
              icon: <Lock className="w-4 h-4 text-amber-600" />,
              bg: 'bg-amber-50',
              title: 'Original Source Immutability',
              body: 'Uploaded legacy repositories in storage/extracted/ remain strictly read-only. All generated code resides in storage/modernized/.',
            },
            {
              icon: <Shield className="w-4 h-4 text-indigo-600" />,
              bg: 'bg-indigo-50',
              title: 'Human-in-the-Loop Governance',
              body: 'No code modification or migration step progresses without explicit human approval state transitions.',
            },
          ].map(({ icon, bg, title, body }) => (
            <div key={title} className="border border-slate-200/80 rounded-xl p-5 space-y-2 bg-slate-50/50">
              <div className={`w-8 h-8 rounded-lg ${bg} border border-slate-200 flex items-center justify-center`}>
                {icon}
              </div>
              <h3 className="text-xs font-extrabold text-slate-900">{title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
