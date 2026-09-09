import { CheckCircle2, Clock, AlertTriangle, RefreshCw } from 'lucide-react'
import type { Repository } from '@/services/api'

interface Props {
  repository: Repository
  onReingest?: () => void
}

const STEPS = [
  { key: 'UPLOADED', label: 'Uploaded' },
  { key: 'VALIDATING', label: 'Validating' },
  { key: 'EXTRACTING', label: 'Extracting' },
  { key: 'INDEXING', label: 'Indexing' },
  { key: 'COMPLETED', label: 'Completed' },
]

export function IngestionProgressCard({ repository, onReingest }: Props) {
  const currentStatus = repository.status
  const isFailed = currentStatus === 'FAILED'

  const getStepState = (stepKey: string) => {
    if (isFailed) {
      return stepKey === 'VALIDATING' ? 'failed' : 'pending'
    }

    const order = ['UPLOADED', 'VALIDATING', 'EXTRACTING', 'INDEXING', 'COMPLETED']
    const currentIndex = order.indexOf(currentStatus)
    const stepIndex = order.indexOf(stepKey)

    if (stepIndex < currentIndex) return 'completed'
    if (stepIndex === currentIndex) return currentStatus === 'COMPLETED' ? 'completed' : 'active'
    return 'pending'
  }

  return (
    <div className="p-6 rounded-xl border border-border bg-card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-foreground">Ingestion Pipeline State</h3>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                currentStatus === 'COMPLETED'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : currentStatus === 'FAILED'
                  ? 'bg-red-500/10 text-red-400 border-red-500/20'
                  : 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse'
              }`}
            >
              {currentStatus}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Explicit state machine transitions governing repository artifact verification and file indexing.
          </p>
        </div>

        {onReingest && (
          <button
            onClick={onReingest}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-ingest
          </button>
        )}
      </div>

      {/* State Machine Steps Visualizer */}
      <div className="grid grid-cols-5 gap-2 pt-2">
        {STEPS.map((step) => {
          const state = getStepState(step.key)
          return (
            <div
              key={step.key}
              className={`p-3 rounded-lg border flex flex-col items-center gap-1 text-center transition-all ${
                state === 'completed'
                  ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400'
                  : state === 'active'
                  ? 'border-blue-500/40 bg-blue-500/10 text-blue-400 font-medium'
                  : state === 'failed'
                  ? 'border-red-500/30 bg-red-500/5 text-red-400'
                  : 'border-border bg-secondary/30 text-muted-foreground opacity-60'
              }`}
            >
              {state === 'completed' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : state === 'active' ? (
                <Clock className="w-4 h-4 text-blue-400 animate-spin" />
              ) : state === 'failed' ? (
                <AlertTriangle className="w-4 h-4 text-red-400" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-current opacity-40" />
              )}
              <span className="text-xs font-medium">{step.label}</span>
            </div>
          )
        })}
      </div>

      {/* Metrics or Failure banner */}
      {repository.latest_ingestion_run && (
        <div className="p-3.5 rounded-lg bg-secondary/50 border border-border/50 text-xs text-muted-foreground flex items-center justify-between">
          <div>
            Discovered{' '}
            <strong className="text-foreground">
              {repository.latest_ingestion_run.files_discovered} files
            </strong>{' '}
            and{' '}
            <strong className="text-foreground">
              {repository.latest_ingestion_run.directories_discovered} directories
            </strong>{' '}
            ({(repository.latest_ingestion_run.bytes_extracted / (1024 * 1024)).toFixed(2)} MB extracted)
          </div>
          {repository.latest_ingestion_run.error_message && (
            <div className="text-red-400 font-medium">
              Error: {repository.latest_ingestion_run.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
