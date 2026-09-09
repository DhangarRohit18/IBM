import React, { useState } from 'react'
import { UserCheck, X } from 'lucide-react'

interface HumanOverrideModalProps {
  isOpen: boolean
  onClose: () => void
  currentStrategy: string
  onSaveOverride: (status: 'REVIEWED' | 'OVERRIDDEN', overrideStrategy?: string, notes?: string) => Promise<void>
}

export const HumanOverrideModal: React.FC<HumanOverrideModalProps> = ({
  isOpen,
  onClose,
  currentStrategy,
  onSaveOverride,
}) => {
  const [actionStatus, setActionStatus] = useState<'REVIEWED' | 'OVERRIDDEN'>('REVIEWED')
  const [overrideStrategy, setOverrideStrategy] = useState<string>('STRANGLER')
  const [notes, setNotes] = useState<string>('')
  const [saving, setSaving] = useState<boolean>(false)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await onSaveOverride(actionStatus, actionStatus === 'OVERRIDDEN' ? overrideStrategy : undefined, notes)
      onClose()
    } catch (err) {
      console.error('Failed to submit strategy audit action', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-lg max-w-md w-full p-6 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-gray-700 pb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-indigo-400" />
              Human Review & Strategy Audit
            </h3>
            <p className="text-[11px] text-gray-400 font-mono mt-0.5">
              Current Recommendation: <span className="text-indigo-300 font-semibold">{currentStrategy}</span>
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-gray-300 mb-1.5">Action Type</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setActionStatus('REVIEWED')}
                className={`py-2 px-3 rounded border text-xs font-semibold ${
                  actionStatus === 'REVIEWED'
                    ? 'bg-emerald-900/60 border-emerald-500 text-emerald-200'
                    : 'bg-gray-900 border-gray-700 text-gray-400'
                }`}
              >
                Approve Recommendation
              </button>

              <button
                type="button"
                onClick={() => setActionStatus('OVERRIDDEN')}
                className={`py-2 px-3 rounded border text-xs font-semibold ${
                  actionStatus === 'OVERRIDDEN'
                    ? 'bg-amber-900/60 border-amber-500 text-amber-200'
                    : 'bg-gray-900 border-gray-700 text-gray-400'
                }`}
              >
                Override Strategy
              </button>
            </div>
          </div>

          {actionStatus === 'OVERRIDDEN' && (
            <div>
              <label className="block font-medium text-gray-300 mb-1">Select Override Strategy</label>
              <select
                value={overrideStrategy}
                onChange={(e) => setOverrideStrategy(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-xs text-white font-mono"
              >
                <option value="MODULARIZE">MODULARIZE</option>
                <option value="EXTRACT_SERVICE">EXTRACT_SERVICE</option>
                <option value="STRANGLER">STRANGLER</option>
                <option value="REFACTOR_IN_PLACE">REFACTOR_IN_PLACE</option>
                <option value="ADAPTER">ADAPTER</option>
                <option value="ANTI_CORRUPTION_LAYER">ANTI_CORRUPTION_LAYER</option>
                <option value="RETAIN_AND_WRAP">RETAIN_AND_WRAP</option>
                <option value="NO_MODERNIZATION_NEEDED">NO_MODERNIZATION_NEEDED</option>
              </select>
            </div>
          )}

          <div>
            <label className="block font-medium text-gray-300 mb-1">Audited Rationale / Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Provide reason for approval or override decision..."
              className="w-full bg-gray-900 border border-gray-700 rounded p-2.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div className="pt-2 flex justify-end gap-2 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded font-semibold text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-semibold text-xs flex items-center gap-1.5"
            >
              {saving ? 'Saving Record...' : 'Record Audited Action'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
