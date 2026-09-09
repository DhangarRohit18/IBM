import React, { useState } from 'react';
import { Search, Filter, ShieldCheck, FileCode, Layers } from 'lucide-react';
import type { CodeEntitySummary } from '../../services/api';

interface ClassListTableProps {
  entities: CodeEntitySummary[];
  selectedEntityId: string | null;
  onSelectEntity: (entityId: string) => void;
  selectedPackage: string | null;
  onSelectPackage: (pkg: string | null) => void;
}

const COMPONENT_BADGES: Record<string, { label: string; bg: string; text: string; border: string }> = {
  CONTROLLER: { label: 'Controller', bg: 'bg-emerald-950/60', text: 'text-emerald-400', border: 'border-emerald-800/60' },
  SERVICE: { label: 'Service', bg: 'bg-blue-950/60', text: 'text-blue-400', border: 'border-blue-800/60' },
  REPOSITORY: { label: 'Repository', bg: 'bg-amber-950/60', text: 'text-amber-400', border: 'border-amber-800/60' },
  ENTITY: { label: 'Entity', bg: 'bg-purple-950/60', text: 'text-purple-400', border: 'border-purple-800/60' },
  CONFIGURATION: { label: 'Config', bg: 'bg-cyan-950/60', text: 'text-cyan-400', border: 'border-cyan-800/60' },
  COMPONENT: { label: 'Component', bg: 'bg-indigo-950/60', text: 'text-indigo-400', border: 'border-indigo-800/60' },
  UTILITY: { label: 'Utility', bg: 'bg-slate-800', text: 'text-slate-300', border: 'border-slate-700' },
  FRAMEWORK_OTHER: { label: 'Other', bg: 'bg-slate-900', text: 'text-slate-400', border: 'border-slate-800' },
};

export const ClassListTable: React.FC<ClassListTableProps> = ({
  entities,
  selectedEntityId,
  onSelectEntity,
  selectedPackage,
  onSelectPackage,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [componentFilter, setComponentFilter] = useState<string>('ALL');

  const filteredEntities = entities.filter((item) => {
    if (selectedPackage && item.package_name !== selectedPackage) return false;
    if (componentFilter !== 'ALL' && item.component_type !== componentFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        item.name.toLowerCase().includes(q) ||
        item.qualified_name.toLowerCase().includes(q) ||
        item.file_path.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden font-mono text-sm">
      {/* Header controls */}
      <div className="p-4 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-950/40">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter classes by name or path..."
            className="w-full bg-slate-900 border border-slate-700 rounded-md pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={componentFilter}
            onChange={(e) => setComponentFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-md px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Categories ({entities.length})</option>
            <option value="CONTROLLER">Controllers</option>
            <option value="SERVICE">Services</option>
            <option value="REPOSITORY">Repositories</option>
            <option value="ENTITY">Entities</option>
            <option value="CONFIGURATION">Configurations</option>
            <option value="COMPONENT">Components</option>
            <option value="UTILITY">Utilities</option>
            <option value="FRAMEWORK_OTHER">Other / Framework</option>
          </select>

          {selectedPackage && (
            <span className="inline-flex items-center px-2 py-1 rounded bg-blue-950/60 border border-blue-800/60 text-blue-300 text-xs">
              Pkg: {selectedPackage}
              <button
                onClick={() => onSelectPackage(null)}
                className="ml-1.5 text-blue-400 hover:text-white"
              >
                ×
              </button>
            </span>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[550px] overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950 text-slate-400 text-[11px] uppercase tracking-wider sticky top-0">
              <th className="py-2.5 px-4 font-semibold">Entity Name</th>
              <th className="py-2.5 px-4 font-semibold">Kind</th>
              <th className="py-2.5 px-4 font-semibold">Classification</th>
              <th className="py-2.5 px-4 font-semibold">Evidence</th>
              <th className="py-2.5 px-4 font-semibold">Structure</th>
              <th className="py-2.5 px-4 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {filteredEntities.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500 italic">
                  No structural entities matching current criteria.
                </td>
              </tr>
            ) : (
              filteredEntities.map((item) => {
                const badge = COMPONENT_BADGES[item.component_type] || COMPONENT_BADGES.FRAMEWORK_OTHER;
                const isSelected = selectedEntityId === item.id;

                return (
                  <tr
                    key={item.id}
                    onClick={() => onSelectEntity(item.id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-blue-900/30 text-slate-100'
                        : 'hover:bg-slate-800/40 text-slate-300'
                    }`}
                  >
                    <td className="py-2.5 px-4">
                      <div className="font-semibold text-slate-200">{item.name}</div>
                      <div className="text-[10px] text-slate-500 truncate max-w-xs">{item.package_name}</div>
                    </td>

                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono bg-slate-800 text-slate-300 border border-slate-700">
                        {item.kind}
                      </span>
                    </td>

                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold border ${badge.bg} ${badge.text} ${badge.border}`}
                      >
                        {badge.label}
                      </span>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="flex items-center space-x-1 text-slate-400">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span className="text-[11px]">
                          {item.classification_evidence.length} fact{item.classification_evidence.length === 1 ? '' : 's'}
                        </span>
                      </div>
                    </td>

                    <td className="py-2.5 px-4">
                      <div className="flex items-center space-x-3 text-[11px] text-slate-400">
                        <span title="Methods count" className="flex items-center space-x-1">
                          <FileCode className="w-3 h-3 text-slate-500" />
                          <span>{item.methods_count}m</span>
                        </span>
                        <span title="Fields count" className="flex items-center space-x-1">
                          <Layers className="w-3 h-3 text-slate-500" />
                          <span>{item.fields_count}f</span>
                        </span>
                      </div>
                    </td>

                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectEntity(item.id);
                        }}
                        className="px-2.5 py-1 rounded text-[11px] bg-slate-800 hover:bg-blue-600 hover:text-white text-slate-300 transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
