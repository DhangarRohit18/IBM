import { Shield, FileText, Hash, HelpCircle, CheckCircle2, AlertTriangle } from 'lucide-react'

interface Props {
  relativeFilePath?: string
  relative_file_path?: string
  lineNumber?: number
  line_number?: number
  sourceConstruct?: string
  source_construct?: string
  evidenceReason?: string
  evidence_reason?: string
  isResolved?: boolean
  is_resolved?: boolean
  onOpenFile?: (path: string, line: number) => void
}

export function SourceEvidenceViewer({
  relativeFilePath,
  relative_file_path,
  lineNumber,
  line_number,
  sourceConstruct,
  source_construct,
  evidenceReason,
  evidence_reason,
  isResolved = true,
  is_resolved,
  onOpenFile,
}: Props) {
  const filePath = relativeFilePath || relative_file_path || ''
  const line = lineNumber ?? line_number ?? 0
  const construct = sourceConstruct || source_construct || ''
  const reason = evidenceReason || evidence_reason || ''
  const resolved = is_resolved !== undefined ? is_resolved : isResolved

  return (
    <div className="p-4 rounded-xl border border-blue-800/60 bg-blue-950/20 space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
          <Shield className="w-4 h-4" /> Deterministic Source Evidence
        </div>
        <span
          className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
            resolved
              ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
              : 'bg-amber-950 text-amber-400 border-amber-800'
          }`}
        >
          {resolved ? (
            <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> VERIFIED SITE</span>
          ) : (
            <span className="flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> AMBIGUOUS SITE</span>
          )}
        </span>
      </div>

      <div className="space-y-1.5 text-xs">
        {filePath && (
          <div className="flex items-center gap-2 font-mono">
            <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span
              onClick={() => onOpenFile?.(filePath, line)}
              className={`truncate ${onOpenFile ? 'text-blue-400 hover:underline cursor-pointer' : 'text-slate-200'}`}
            >
              {filePath}
            </span>
            <span className="flex items-center gap-0.5 text-slate-400 shrink-0">
              <Hash className="w-3 h-3" /> Line {line}
            </span>
          </div>
        )}

        {construct && (
          <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-emerald-400 truncate">
            {construct}
          </div>
        )}

        {reason && (
          <div className="flex items-start gap-1.5 text-slate-400 text-[11px]">
            <HelpCircle className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
            <span>{reason}</span>
          </div>
        )}
      </div>
    </div>
  )
}
