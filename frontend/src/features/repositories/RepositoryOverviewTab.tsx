import { Shield, FileText, HardDrive, Cpu, CheckCircle } from 'lucide-react'
import type { Repository, RepositoryManifest } from '@/services/api'

interface Props {
  repository: Repository
  manifest: RepositoryManifest | null
}

export function RepositoryOverviewTab({ repository, manifest }: Props) {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="space-y-6">
      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground mb-1">
            <HardDrive className="w-4 h-4 text-primary" /> Original Artifact Size
          </div>
          <div className="text-xl font-bold text-foreground">{formatBytes(repository.artifact_size)}</div>
          <div className="text-[11px] text-muted-foreground mt-1 truncate">{repository.original_filename}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground mb-1">
            <FileText className="w-4 h-4 text-emerald-400" /> Discovered Files
          </div>
          <div className="text-xl font-bold text-foreground">
            {manifest ? manifest.summary.total_files : '—'}
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">
            {manifest ? `${manifest.summary.total_directories} Directories` : 'Indexing...'}
          </div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground mb-1">
            <Cpu className="w-4 h-4 text-blue-400" /> Technologies Detected
          </div>
          <div className="text-xl font-bold text-foreground">
            {manifest ? manifest.technologies.length : 0}
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">Evidence-backed detection</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground mb-1">
            <Shield className="w-4 h-4 text-amber-400" /> SHA-256 Checksum
          </div>
          <div className="text-xs font-mono font-bold text-foreground truncate" title={repository.sha256}>
            {repository.sha256.substring(0, 16)}...
          </div>
          <div className="text-[11px] text-emerald-400 mt-1">Immutable Verification Key</div>
        </div>
      </div>

      {/* Technology Detection Section */}
      <div className="p-6 rounded-xl border border-border bg-card space-y-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">Deterministic Technology Detection</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Facts established strictly by static analysis of repository files and build descriptors. No AI inference.
          </p>
        </div>

        {manifest && manifest.technologies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {manifest.technologies.map((tech) => (
              <div
                key={tech.name}
                className="p-4 rounded-lg border border-border/80 bg-secondary/20 space-y-2"
              >
                <div className="flex items-center gap-2 font-semibold text-sm text-foreground">
                  <CheckCircle className="w-4 h-4 text-primary" /> {tech.name}
                </div>
                <ul className="space-y-1">
                  {tech.evidence.map((ev, idx) => (
                    <li key={idx} className="text-xs text-muted-foreground flex items-start gap-1.5 font-mono">
                      <span className="text-primary font-bold">›</span> {ev}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-muted-foreground border border-dashed border-border rounded-lg">
            No technologies detected or manifest not generated.
          </div>
        )}
      </div>

      {/* Key Project Files */}
      {manifest && manifest.key_files.length > 0 && (
        <div className="p-6 rounded-xl border border-border bg-card space-y-3">
          <h3 className="text-base font-semibold text-foreground">Key Project Files</h3>
          <div className="flex flex-wrap gap-2">
            {manifest.key_files.map((file) => (
              <span
                key={file}
                className="px-3 py-1 rounded-md border border-border bg-secondary/50 text-xs font-mono text-foreground"
              >
                {file}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
