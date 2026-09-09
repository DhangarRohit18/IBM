import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Play,
  Layers,
  FileCode,
  GitFork,
  Search,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Info
} from 'lucide-react';
import { api, type AnalysisRun, type CodeAnalysisSummary, type CodeGraphData, type CodeEntityDetail } from '../../services/api';
import { PackageTree } from './PackageTree';
import { ClassListTable } from './ClassListTable';
import { ArchitectureGraph } from './ArchitectureGraph';
import { SearchPanel } from './SearchPanel';
import { ClassDetailPanel } from './ClassDetailPanel';

interface SystemXRayPageProps {
  repositoryId: string;
}

type TabType = 'overview' | 'classes' | 'relationships' | 'search';

export const SystemXRayPage: React.FC<SystemXRayPageProps> = ({ repositoryId }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [analysisRun, setAnalysisRun] = useState<AnalysisRun | null>(null);
  const [summary, setSummary] = useState<CodeAnalysisSummary | null>(null);
  const [graphData, setGraphData] = useState<CodeGraphData | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [triggering, setTriggering] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Filters and selection state
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedEntityDetail, setSelectedEntityDetail] = useState<CodeEntityDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const fetchAnalysisData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Check for latest analysis run
      const runs = await api.analysis.listRuns(repositoryId);
      if (runs.length === 0) {
        setAnalysisRun(null);
        setSummary(null);
        setGraphData(null);
        setLoading(false);
        return;
      }

      const latestRun = runs[0];
      setAnalysisRun(latestRun);

      if (latestRun.status === 'COMPLETED') {
        const [sumRes, graphRes] = await Promise.all([
          api.analysis.getSummary(latestRun.id),
          api.analysis.getGraph(latestRun.id),
        ]);
        setSummary(sumRes);
        setGraphData(graphRes);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load analysis data');
    } finally {
      setLoading(false);
    }
  }, [repositoryId]);

  useEffect(() => {
    fetchAnalysisData();
  }, [fetchAnalysisData]);

  // Handle entity detail inspection
  useEffect(() => {
    if (!selectedEntityId) {
      setSelectedEntityDetail(null);
      return;
    }

    let isMounted = true;
    setLoadingDetail(true);

    api.analysis
      .getClassDetail(selectedEntityId)
      .then((detail) => {
        if (isMounted) {
          setSelectedEntityDetail(detail);
          setLoadingDetail(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load class detail:', err);
        if (isMounted) setLoadingDetail(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedEntityId]);

  const handleStartAnalysis = async () => {
    try {
      setTriggering(true);
      setError(null);
      const run = await api.analysis.trigger(repositoryId);
      setAnalysisRun(run);
      
      // Poll until completion or failure
      const interval = setInterval(async () => {
        try {
          const statusRes = await api.analysis.getRun(run.id);
          setAnalysisRun(statusRes);
          if (statusRes.status === 'COMPLETED' || statusRes.status === 'FAILED') {
            clearInterval(interval);
            setTriggering(false);
            fetchAnalysisData();
          }
        } catch (e) {
          clearInterval(interval);
          setTriggering(false);
        }
      }, 1500);

    } catch (err: any) {
      setError(err.message || 'Failed to start analysis run');
      setTriggering(false);
    }
  };

  if (loading && !analysisRun) {
    return (
      <div className="p-8 text-center font-mono text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
        <p className="text-sm">Loading System X-Ray metadata...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-mono text-slate-100">
      {/* Top Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
              <Activity className="w-6 h-6 text-blue-400" />
              <span>System X-Ray — Deterministic Structural Analysis</span>
            </h1>
            {analysisRun && (
              <span
                className={`px-2.5 py-0.5 rounded text-xs font-semibold uppercase border ${
                  analysisRun.status === 'COMPLETED'
                    ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                    : analysisRun.status === 'RUNNING'
                    ? 'bg-blue-950/80 text-blue-300 border-blue-800 animate-pulse'
                    : analysisRun.status === 'FAILED'
                    ? 'bg-red-950/80 text-red-300 border-red-800'
                    : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                {analysisRun.status}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Deterministic AST extraction preserving full line numbers, component evidence reasons, and conservative call site resolution. Zero AI inference.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchAnalysisData}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md text-xs flex items-center space-x-1 border border-slate-700"
            title="Refresh Analysis Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleStartAnalysis}
            disabled={triggering || (analysisRun?.status === 'RUNNING')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-md text-xs font-semibold flex items-center space-x-2 transition-colors shadow-lg shadow-blue-900/30"
          >
            {triggering || analysisRun?.status === 'RUNNING' ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analyzing Repository...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run System X-Ray</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-950/80 border border-red-800 text-red-300 rounded-lg text-xs flex items-start space-x-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* No Analysis State */}
      {!analysisRun && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center space-y-4">
          <Activity className="w-12 h-12 text-slate-600 mx-auto" />
          <h2 className="text-base font-semibold text-slate-200">No Analysis Run Detected</h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click "Run System X-Ray" above to execute deterministic static analysis on the ingested repository artifact.
          </p>
          <button
            onClick={handleStartAnalysis}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-xs font-semibold inline-flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>Start Deterministic Analysis</span>
          </button>
        </div>
      )}

      {/* Completed Metrics Summary Banner */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Packages</span>
            <div className="text-lg font-bold text-slate-100">{summary.total_packages}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Classes</span>
            <div className="text-lg font-bold text-blue-400">{summary.total_classes}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Methods</span>
            <div className="text-lg font-bold text-cyan-400">{summary.total_methods}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Fields</span>
            <div className="text-lg font-bold text-amber-400">{summary.total_fields}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Relationships</span>
            <div className="text-lg font-bold text-purple-400">{summary.total_relationships}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-center">
            <span className="text-[10px] text-slate-500 uppercase">Call Resolution</span>
            <div className="text-lg font-bold text-emerald-400">
              {summary.calls_resolution.resolved}/{summary.calls_resolution.total}
            </div>
          </div>
        </div>
      )}

      {/* Tabs Bar */}
      {analysisRun?.status === 'COMPLETED' && summary && (
        <div className="space-y-4">
          <div className="flex border-b border-slate-800 space-x-6 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-2 flex items-center space-x-2 border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <GitFork className="w-4 h-4" />
              <span>Architecture Graph</span>
            </button>

            <button
              onClick={() => setActiveTab('classes')}
              className={`pb-2 flex items-center space-x-2 border-b-2 transition-colors ${
                activeTab === 'classes'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileCode className="w-4 h-4" />
              <span>Packages & Classes ({summary.total_classes})</span>
            </button>

            <button
              onClick={() => setActiveTab('relationships')}
              className={`pb-2 flex items-center space-x-2 border-b-2 transition-colors ${
                activeTab === 'relationships'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Relationships & Traceability</span>
            </button>

            <button
              onClick={() => setActiveTab('search')}
              className={`pb-2 flex items-center space-x-2 border-b-2 transition-colors ${
                activeTab === 'search'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Entity Search</span>
            </button>
          </div>

          {/* Tab 1: Architecture Graph */}
          {activeTab === 'overview' && graphData && (
            <div className="space-y-4">
              <ArchitectureGraph
                graphData={graphData}
                onSelectEntity={(id) => setSelectedEntityId(id)}
              />
            </div>
          )}

          {/* Tab 2: Packages & Classes */}
          {activeTab === 'classes' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
              <div className="lg:col-span-1">
                <PackageTree
                  packages={summary.packages}
                  selectedPackage={selectedPackage}
                  onSelectPackage={(pkg) => setSelectedPackage(pkg)}
                />
              </div>
              <div className="lg:col-span-3">
                <ClassListTable
                  entities={summary.classes}
                  selectedEntityId={selectedEntityId}
                  onSelectEntity={(id) => setSelectedEntityId(id)}
                  selectedPackage={selectedPackage}
                  onSelectPackage={(pkg) => setSelectedPackage(pkg)}
                />
              </div>
            </div>
          )}

          {/* Tab 3: Relationships & Evidence */}
          {activeTab === 'relationships' && (
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 font-mono text-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">
                  Extracted Relationships ({summary.relationships_breakdown.reduce((a, b) => a + b.count, 0)})
                </h3>
                <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Conservative resolution preserved</span>
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
                {summary.relationships_breakdown.map((item) => (
                  <div key={item.type} className="bg-slate-950 border border-slate-800 p-2.5 rounded text-center">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">{item.type}</span>
                    <div className="text-base font-bold text-cyan-300 mt-0.5">{item.count}</div>
                  </div>
                ))}
              </div>

              <div className="p-3 bg-blue-950/40 border border-blue-800/60 rounded text-xs text-blue-300 flex items-start space-x-2">
                <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-blue-400" />
                <span>
                  Ambiguous method calls without unambiguous single target remain marked as <strong>UNRESOLVED</strong> with line-level call site evidence attached.
                </span>
              </div>
            </div>
          )}

          {/* Tab 4: Search */}
          {activeTab === 'search' && (
            <SearchPanel
              analysisRunId={analysisRun.id}
              onSelectEntity={(id) => setSelectedEntityId(id)}
            />
          )}
        </div>
      )}

      {/* Class Detail Modal / Panel Overlay */}
      {selectedEntityId && (
        <ClassDetailPanel
          entityDetail={selectedEntityDetail}
          loading={loadingDetail}
          onClose={() => setSelectedEntityId(null)}
        />
      )}
    </div>
  );
};
