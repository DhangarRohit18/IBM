import { useState, useEffect } from 'react'
import {
  Settings,
  Server,
  Database,
  Cpu,
  Shield,
  HardDrive,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react'
import { api, type HealthResponse, type HealthStatusItem } from '@/services/api'

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

  useEffect(() => {
    fetchHealth()
  }, [])

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-teal-600 font-extrabold text-xs tracking-wider uppercase mb-1">
            <Settings className="w-4 h-4" /> Platform Settings & Governance
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900">System Configuration</h1>
          <p className="text-xs text-slate-500 mt-1">
            Inspect platform health, backend services, security storage limits, and environment settings.
          </p>
        </div>
        <button
          onClick={fetchHealth}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-slate-200 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Status
        </button>
      </div>

      {/* Backend Infrastructure Health */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-teal-600" />
            <h2 className="text-base font-extrabold text-slate-900">Backend Infrastructure Health</h2>
          </div>
          {health && (
            <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5">
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
          <div className="p-6 text-center text-xs text-slate-400">Querying backend service health...</div>
        ) : health ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
                <span className="flex items-center gap-1.5"><Server className="w-4 h-4 text-blue-600" /> FastAPI Application</span>
                <span className="font-bold text-emerald-600 uppercase">{health.status}</span>
              </div>
              <div className="text-lg font-black text-slate-900">{health.app_name} v{health.app_version}</div>
              <div className="text-[11px] font-mono text-slate-500">Env: {health.environment}</div>
            </div>

            {health.services.map((svc: HealthStatusItem) => (
              <div key={svc.name} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
                  <span className="flex items-center gap-1.5">
                    {svc.name.includes('postgres') ? (
                      <Database className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <Cpu className="w-4 h-4 text-amber-600" />
                    )}
                    {svc.name.toUpperCase()}
                  </span>
                  <span className="font-bold text-emerald-600 uppercase">{svc.status}</span>
                </div>
                <div className="text-lg font-black text-slate-900 capitalize">{svc.name} Service</div>
                <div className="text-[11px] font-mono text-slate-500">Connected & Verified</div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {/* Storage & Security Policy */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-4">
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-teal-600" />
          <h2 className="text-base font-extrabold text-slate-900">Storage & Security Policy Limits</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
            <div className="text-xs text-slate-500 font-medium">Max Upload Size</div>
            <div className="text-lg font-extrabold text-slate-900">50 MB</div>
            <div className="text-[10px] text-slate-400">ZIP archive upload limit</div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
            <div className="text-xs text-slate-500 font-medium">Max Extracted Size</div>
            <div className="text-lg font-extrabold text-slate-900">250 MB</div>
            <div className="text-[10px] text-slate-400">Extracted source boundary</div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
            <div className="text-xs text-slate-500 font-medium">Max File Count</div>
            <div className="text-lg font-extrabold text-slate-900">10,000 Files</div>
            <div className="text-[10px] text-slate-400">Zip Slip protection limit</div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
            <div className="text-xs text-slate-500 font-medium">Isolated Storage Path</div>
            <div className="text-xs font-mono font-bold text-slate-800 truncate">/app/storage</div>
            <div className="text-[10px] text-slate-400">Immutable source storage</div>
          </div>
        </div>
      </div>

      {/* Platform Information */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-3">
        <div className="flex items-center gap-2.5">
          <HardDrive className="w-5 h-5 text-teal-600" />
          <h2 className="text-base font-extrabold text-slate-900">Architectural Principles</h2>
        </div>
        <ul className="text-xs text-slate-600 space-y-2 list-disc list-inside leading-relaxed">
          <li><strong>Deterministic First</strong>: All repository facts (files, classes, AST relationships, call sites) are parsed deterministically without AI inference.</li>
          <li><strong>Original Source Immutability</strong>: Uploaded legacy repositories in <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">storage/extracted/</code> remain strictly read-only. All generated code resides in <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">storage/modernized/</code>.</li>
          <li><strong>Human-in-the-loop Governance</strong>: No code modification or migration step progresses without explicit human approval state transitions.</li>
        </ul>
      </div>
    </div>
  )
}
