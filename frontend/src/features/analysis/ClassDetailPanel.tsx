import React from 'react';
import { FileText, ArrowRight, CheckCircle2, X } from 'lucide-react';
import type { CodeEntityDetail } from '../../services/api';
import { SourceEvidenceViewer } from './SourceEvidenceViewer';

interface ClassDetailPanelProps {
  entityDetail: CodeEntityDetail | null;
  loading: boolean;
  onClose: () => void;
}

export const ClassDetailPanel: React.FC<ClassDetailPanelProps> = ({
  entityDetail,
  loading,
  onClose,
}) => {
  if (loading) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 max-w-lg w-full text-center font-mono">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-sm text-slate-300">Loading deterministic entity inspection data...</p>
        </div>
      </div>
    );
  }

  if (!entityDetail) return null;

  const { entity, methods, fields, outgoing_relationships, incoming_relationships } = entityDetail;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col font-mono text-sm shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-blue-950 text-blue-300 border border-blue-800">
                {entity.entity_type}
              </span>
              <h2 className="text-base font-bold text-slate-100">{entity.name}</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xl">{entity.fully_qualified_name}</p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Classification Evidence Banner */}
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Component Classification Fact Trace
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800">
                {entity.component_type}
              </span>
            </div>

            <div className="space-y-1.5">
              {entity.classification_evidence.map((fact, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{fact}</span>
                </div>
              ))}
            </div>
          </div>

          {/* File location */}
          <div className="flex items-center justify-between text-xs text-slate-400 bg-slate-950/50 p-3 rounded border border-slate-800">
            <span className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>{entity.relative_file_path}</span>
            </span>
            <span>Lines {entity.line_start} - {entity.line_end}</span>
          </div>

          {/* Extends / Implements */}
          {(entity.extends_name || entity.implements_names.length > 0) && (
            <div className="space-y-2 text-xs">
              <h4 className="font-semibold text-slate-400 uppercase tracking-wider text-[11px]">Type Hierarchy</h4>
              {entity.extends_name && (
                <div className="text-slate-300">
                  <span className="text-purple-400 font-semibold">Extends:</span> {entity.extends_name}
                </div>
              )}
              {entity.implements_names.length > 0 && (
                <div className="text-slate-300">
                  <span className="text-amber-400 font-semibold">Implements:</span> {entity.implements_names.join(', ')}
                </div>
              )}
            </div>
          )}

          {/* Methods */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2">
              Declared Methods ({methods.length})
            </h4>
            {methods.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No method declarations extracted.</p>
            ) : (
              <div className="space-y-2">
                {methods.map((m) => (
                  <div key={m.id} className="p-3 bg-slate-950 border border-slate-800 rounded font-mono text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-cyan-300">
                        {m.name}({m.parameters.map((p) => `${p.type} ${p.name}`).join(', ')}) : {m.return_type}
                      </span>
                      <span className="text-[10px] text-slate-500">L{m.line_start}-L{m.line_end}</span>
                    </div>
                    {m.annotations.length > 0 && (
                      <div className="text-[11px] text-slate-400">
                        {m.annotations.map((a) => `@${a.name}`).join(' ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Fields */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2">
              Declared Fields ({fields.length})
            </h4>
            {fields.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No field declarations extracted.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {fields.map((f) => (
                  <div key={f.id} className="p-2.5 bg-slate-950 border border-slate-800 rounded font-mono text-xs">
                    <div className="font-bold text-amber-300">{f.field_type} {f.name}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Line {f.line_start}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Relationships Outgoing & Incoming */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2">
              Structural Relationships ({outgoing_relationships.length + incoming_relationships.length})
            </h4>

            <div className="space-y-3">
              {outgoing_relationships.map((rel) => (
                <div key={rel.id} className="p-3 bg-slate-950 border border-slate-800 rounded space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-blue-400">{entity.name}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-bold text-slate-200">{rel.target_entity_name}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-cyan-300 font-bold border border-slate-700">
                      {rel.relationship_type}
                    </span>
                  </div>

                  <SourceEvidenceViewer
                    relative_file_path={rel.relative_file_path}
                    line_number={rel.line_number}
                    source_construct={rel.source_construct}
                    evidence_reason={rel.evidence_reason}
                    is_resolved={rel.is_resolved}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
