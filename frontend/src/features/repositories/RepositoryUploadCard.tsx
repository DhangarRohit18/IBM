import { useState, useRef } from 'react'
import { UploadCloud, AlertCircle, FileArchive, CheckCircle2 } from 'lucide-react'
import { api, isApiError } from '@/services/api'

interface Props {
  projectId: string
  onUploadSuccess: () => void
}

export function RepositoryUploadCard({ projectId, onUploadSuccess }: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.zip')) {
      setError('INVALID_FILE_TYPE: Only ZIP repository archives (.zip) are supported.')
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      await api.projects.uploadRepository(projectId, file)
      onUploadSuccess()
    } catch (err: unknown) {
      if (isApiError(err) && typeof err.body === 'object' && err.body && 'detail' in err.body) {
        setError(String((err.body as { detail: string }).detail))
      } else {
        setError('Upload failed. Please verify the ZIP file and try again.')
      }
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  return (
    <div className="p-6 rounded-xl border border-border bg-card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Upload Application Repository</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Select or drop a ZIP archive of your legacy source code. Original artifacts remain immutable.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-lg bg-destructive/10 border border-destructive/20 flex items-start gap-2 text-destructive text-xs font-medium">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
          isDragging
            ? 'border-primary bg-primary/5 scale-[1.01]'
            : 'border-border hover:border-primary/50 hover:bg-accent/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileSelect(e.target.files[0])
            }
          }}
          className="hidden"
        />

        <div className="p-3 rounded-full bg-primary/10 text-primary">
          <UploadCloud className="w-8 h-8" />
        </div>

        <div>
          <p className="text-sm font-medium text-foreground">
            {isUploading ? 'Uploading & Ingesting Repository...' : 'Click to upload or drag & drop ZIP'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Max upload size: 50MB. Max file count: 10,000 files.
          </p>
        </div>

        {isUploading && (
          <div className="flex items-center gap-2 text-xs font-medium text-primary animate-pulse mt-2">
            <FileArchive className="w-4 h-4" /> Processing repository extraction & indexing...
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 pt-2 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Immutable Original Storage
        </div>
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Zip Slip Protection
        </div>
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Deterministic Detection
        </div>
      </div>
    </div>
  )
}
