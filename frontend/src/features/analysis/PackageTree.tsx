import React, { useState } from 'react';
import { Folder, FolderOpen, ChevronRight, ChevronDown, FileCode } from 'lucide-react';
import type { CodePackage } from '../../services/api';

interface PackageTreeProps {
  packages: CodePackage[];
  selectedPackage: string | null;
  onSelectPackage: (packageName: string | null) => void;
}

export const PackageTree: React.FC<PackageTreeProps> = ({
  packages,
  selectedPackage,
  onSelectPackage,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  const toggleExpand = (pkgName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedNodes(prev => ({ ...prev, [pkgName]: !prev[pkgName] }));
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 font-mono text-sm">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
        <h3 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">Packages ({packages.length})</h3>
        {selectedPackage && (
          <button
            onClick={() => onSelectPackage(null)}
            className="text-xs text-blue-400 hover:underline"
          >
            Clear Filter
          </button>
        )}
      </div>

      <div className="space-y-1 max-h-[400px] overflow-y-auto pr-1">
        {packages.length === 0 ? (
          <p className="text-slate-500 text-xs py-2 italic">No packages detected.</p>
        ) : (
          packages.map((pkg) => {
            const isSelected = selectedPackage === pkg.name;
            const isExpanded = expandedNodes[pkg.name] ?? true;

            return (
              <div key={pkg.id} className="select-none">
                <div
                  onClick={() => onSelectPackage(isSelected ? null : pkg.name)}
                  className={`flex items-center justify-between px-2.5 py-1.5 rounded cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-blue-900/40 text-blue-300 border border-blue-700/50'
                      : 'hover:bg-slate-800/60 text-slate-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 truncate">
                    <button
                      onClick={(e) => toggleExpand(pkg.name, e)}
                      className="p-0.5 hover:bg-slate-700 rounded text-slate-400"
                    >
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>
                    {isExpanded ? (
                      <FolderOpen className="w-4 h-4 text-amber-400 flex-shrink-0" />
                    ) : (
                      <Folder className="w-4 h-4 text-amber-500 flex-shrink-0" />
                    )}
                    <span className="truncate text-xs font-mono">{pkg.name}</span>
                  </div>
                  <span className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 flex-shrink-0 border border-slate-700/50">
                    <FileCode className="w-3 h-3 text-slate-400" />
                    <span>{pkg.entity_count}</span>
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
