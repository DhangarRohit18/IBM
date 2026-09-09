import React, { useState } from 'react';
import { Search, FileCode, Layers, Code, ShieldCheck, ArrowRight } from 'lucide-react';
import { api, type AnalysisSearchResult } from '../../services/api';

interface SearchPanelProps {
  analysisRunId: string;
  onSelectEntity: (entityId: string) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({
  analysisRunId,
  onSelectEntity,
}) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const res = await api.analysis.search(analysisRunId, query.trim());
      setResults(res);
    } catch (err: any) {
      setError(err.message || 'Failed to search structural entities');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 font-mono text-sm space-y-6">
      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="space-y-2">
        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Deterministic Structural Entity Search
        </label>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search classes, methods (e.g. processPayment), fields, or annotations..."
              className="w-full bg-slate-950 border border-slate-700 rounded-md pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-md text-xs font-semibold flex items-center space-x-1.5 transition-colors"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        <p className="text-[11px] text-slate-500 flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Searches only exact AST-derived structural declarations and metadata.</span>
        </p>
      </form>

      {error && (
        <div className="p-3 bg-red-950/60 border border-red-800 text-red-300 rounded text-xs">
          {error}
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-6 pt-2 border-t border-slate-800">
          {/* Classes Results */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <FileCode className="w-4 h-4 text-blue-400" />
              <span>Matching Classes ({results.classes.length})</span>
            </h4>
            {results.classes.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-1">No matching classes found.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {results.classes.map((cls) => (
                  <div
                    key={cls.id}
                    onClick={() => onSelectEntity(cls.id)}
                    className="p-3 bg-slate-950 border border-slate-800 hover:border-blue-700/60 rounded cursor-pointer transition-colors flex items-center justify-between group"
                  >
                    <div>
                      <div className="font-semibold text-slate-200 text-xs group-hover:text-blue-300">
                        {cls.name}
                      </div>
                      <div className="text-[10px] text-slate-500 truncate">{cls.package_name}</div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 transition-colors" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Methods Results */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Code className="w-4 h-4 text-cyan-400" />
              <span>Matching Methods ({results.methods.length})</span>
            </h4>
            {results.methods.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-1">No matching methods found.</p>
            ) : (
              <div className="space-y-1.5">
                {results.methods.map((m) => (
                  <div
                    key={m.id}
                    onClick={() => onSelectEntity(m.entity_id)}
                    className="p-2.5 bg-slate-950 border border-slate-800 hover:border-cyan-700/60 rounded cursor-pointer transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="font-mono text-xs text-cyan-300 font-semibold">
                        {m.name}({m.parameters.map((p) => p.type).join(', ')}) : {m.return_type}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        File: {m.file_path} {m.line_number && `(L${m.line_number})`}
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400">
                      Line {m.line_number || 'N/A'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Fields Results */}
          <div>
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Layers className="w-4 h-4 text-amber-400" />
              <span>Matching Fields ({results.fields.length})</span>
            </h4>
            {results.fields.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-1">No matching fields found.</p>
            ) : (
              <div className="space-y-1.5">
                {results.fields.map((f) => (
                  <div
                    key={f.id}
                    onClick={() => onSelectEntity(f.entity_id)}
                    className="p-2.5 bg-slate-950 border border-slate-800 hover:border-amber-700/60 rounded cursor-pointer transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="font-mono text-xs text-amber-300 font-semibold">
                        {f.field_type} {f.name}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        File: {f.file_path} {f.line_number && `(L${f.line_number})`}
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400">
                      Line {f.line_number || 'N/A'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
