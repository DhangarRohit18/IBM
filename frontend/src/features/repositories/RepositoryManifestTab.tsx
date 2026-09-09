import { useState } from 'react'
import { Code, Copy, Check } from 'lucide-react'
import type { RepositoryManifest } from '@/services/api'

interface Props {
  manifest: RepositoryManifest | null
}

export function RepositoryManifestTab({ manifest }: Props) {
  const [copied, setCopied] = useState(false)

  if (!manifest) {
    return (
      <div className="p-12 text-center text-xs text-muted-foreground border border-dashed border-border rounded-xl">
        Manifest data is loading or not available.
      </div>
    )
  }

  const jsonString = JSON.stringify(manifest, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* File Extension Breakdown */}
      <div className="p-6 rounded-xl border border-border bg-card space-y-4">
        <h3 className="text-base font-semibold text-foreground">File Extension Breakdown</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
          {Object.entries(manifest.extension_breakdown).map(([ext, count]) => (
            <div key={ext} className="p-3 rounded-lg border border-border bg-secondary/30 text-center">
              <div className="text-sm font-mono font-bold text-primary">{ext || '(none)'}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{count} files</div>
            </div>
          ))}
        </div>
      </div>

      {/* Raw JSON Manifest Viewer */}
      <div className="p-6 rounded-xl border border-border bg-card space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code className="w-4 h-4 text-primary" />
            <h3 className="text-base font-semibold text-foreground">Canonical Manifest Object</h3>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy JSON'}
          </button>
        </div>

        <pre className="p-4 rounded-lg border border-border bg-black/50 text-emerald-400 font-mono text-xs overflow-x-auto max-h-[500px] leading-relaxed">
          {jsonString}
        </pre>
      </div>
    </div>
  )
}
