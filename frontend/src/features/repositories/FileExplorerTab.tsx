import { useEffect, useState } from 'react'
import { Folder, File, ChevronRight, ChevronDown, FileText, AlertCircle } from 'lucide-react'
import { api, type RepositoryFile, type FileContentResponse, isApiError } from '@/services/api'

interface Props {
  repositoryId: string
}

interface TreeNode {
  name: string
  path: string
  isDir: boolean
  size?: number
  children: Record<string, TreeNode>
}

export function FileExplorerTab({ repositoryId }: Props) {
  const [files, setFiles] = useState<RepositoryFile[]>([])
  const [tree, setTree] = useState<TreeNode | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<FileContentResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [contentLoading, setContentLoading] = useState(false)
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set(['root']))
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const fileList = await api.repositories.files(repositoryId)
        setFiles(fileList)
        buildTree(fileList)
      } catch (err) {
        setError('Failed to load repository files.')
      } finally {
        setLoading(false)
      }
    }
    fetchFiles()
  }, [repositoryId])

  const buildTree = (fileList: RepositoryFile[]) => {
    const root: TreeNode = { name: 'root', path: '', isDir: true, children: {} }

    fileList.forEach((file) => {
      const parts = file.relative_path.split('/')
      let current = root

      parts.forEach((part, index) => {
        const isLast = index === parts.length - 1
        const currentPath = parts.slice(0, index + 1).join('/')

        if (!current.children[part]) {
          current.children[part] = {
            name: part,
            path: currentPath,
            isDir: !isLast || file.is_directory,
            size: isLast ? file.size_bytes : undefined,
            children: {},
          }
        }
        current = current.children[part]
      })
    })

    setTree(root)
  }

  const handleSelectFile = async (path: string) => {
    setSelectedFile(path)
    setContentLoading(true)
    setError(null)
    try {
      const res = await api.repositories.fileContent(repositoryId, path)
      setFileContent(res)
    } catch (err: unknown) {
      if (isApiError(err) && typeof err.body === 'object' && err.body && 'detail' in err.body) {
        setError(String((err.body as { detail: string }).detail))
      } else {
        setError('Failed to load file content.')
      }
      setFileContent(null)
    } finally {
      setContentLoading(false)
    }
  }

  const toggleExpand = (path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }

  const renderTreeNodes = (node: TreeNode, depth: number = 0) => {
    const sortedKeys = Object.keys(node.children).sort((a, b) => {
      const nodeA = node.children[a]
      const nodeB = node.children[b]
      if (nodeA.isDir && !nodeB.isDir) return -1
      if (!nodeA.isDir && nodeB.isDir) return 1
      return a.localeCompare(b)
    })

    return sortedKeys.map((key) => {
      const child = node.children[key]
      const isExpanded = expandedPaths.has(child.path)
      const isSelected = selectedFile === child.path

      return (
        <div key={child.path} style={{ paddingLeft: `${depth * 12}px` }}>
          {child.isDir ? (
            <div>
              <button
                onClick={() => toggleExpand(child.path)}
                className="w-full flex items-center gap-1.5 py-1 px-2 rounded-md hover:bg-accent/50 text-xs text-foreground font-medium transition-colors"
              >
                {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" /> : <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />}
                <Folder className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                <span className="truncate">{child.name}</span>
              </button>
              {isExpanded && <div>{renderTreeNodes(child, depth + 1)}</div>}
            </div>
          ) : (
            <button
              onClick={() => handleSelectFile(child.path)}
              className={`w-full flex items-center justify-between py-1 px-2 rounded-md text-xs font-mono transition-colors ${
                isSelected ? 'bg-primary/20 text-primary font-semibold' : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground'
              }`}
            >
              <div className="flex items-center gap-1.5 truncate">
                <File className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                <span className="truncate">{child.name}</span>
              </div>
              {child.size !== undefined && (
                <span className="text-[10px] text-muted-foreground/70 shrink-0 ml-2">
                  {child.size < 1024 ? `${child.size}B` : `${(child.size / 1024).toFixed(0)}KB`}
                </span>
              )}
            </button>
          )}
        </div>
      )
    })
  }

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-foreground">Loading file tree...</div>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 min-h-[550px]">
      {/* File Tree Panel */}
      <div className="md:col-span-4 p-4 rounded-xl border border-border bg-card overflow-y-auto max-h-[600px] space-y-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          Repository Tree ({files.length} items)
        </h3>
        {tree ? renderTreeNodes(tree) : <div className="text-xs text-muted-foreground">No files</div>}
      </div>

      {/* Source Code Preview Panel */}
      <div className="md:col-span-8 p-4 rounded-xl border border-border bg-card flex flex-col min-h-[500px]">
        {selectedFile ? (
          <div className="space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-border text-xs font-mono">
              <span className="font-semibold text-foreground truncate">{selectedFile}</span>
              {fileContent && (
                <span className="text-muted-foreground shrink-0 ml-2">
                  {(fileContent.size_bytes / 1024).toFixed(1)} KB {fileContent.is_truncated && '(Truncated preview)'}
                </span>
              )}
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4" /> {error}
              </div>
            )}

            {contentLoading ? (
              <div className="flex-1 flex items-center justify-center text-xs text-muted-foreground">
                Loading source text...
              </div>
            ) : fileContent ? (
              <pre className="flex-1 p-4 rounded-lg bg-black/60 border border-border font-mono text-xs text-foreground overflow-x-auto leading-relaxed max-h-[500px]">
                {fileContent.content}
              </pre>
            ) : null}
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-muted-foreground">
            <FileText className="w-12 h-12 mb-2 opacity-40" />
            <p className="text-sm font-medium text-foreground">Select a file from the repository tree</p>
            <p className="text-xs mt-1 max-w-xs">
              Click on any source or configuration file to inspect its raw text content.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
