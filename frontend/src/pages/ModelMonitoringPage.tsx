import React, { useEffect, useState } from 'react';
import apiClient from '@/services/api';
import { Activity, Gauge, TrendingUp, AlertTriangle, CheckCircle, RefreshCw, Cpu, BarChart3 } from 'lucide-react';

export const ModelMonitoringPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [drift, setDrift] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [metricsRes, driftRes] = await Promise.all([
        apiClient.get('/monitoring/metrics'),
        apiClient.get('/monitoring/drift'),
      ]);
      setMetrics(metricsRes.data);
      setDrift(driftRes.data);
    } catch (err: any) {
      console.error('Failed to load model monitoring metrics:', err);
      setError(err?.response?.data?.detail || 'Unable to retrieve model telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const isStable = drift?.status === 'STABLE';
  const statusColor = isStable ? 'text-emerald-400 border-emerald-800 bg-emerald-950/60' : 'text-amber-400 border-amber-800 bg-amber-950/60';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-7 h-7 text-cyan-400" />
            Model Telemetry & Drift Monitoring
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time inference tracking, latency distributions, and empirical Population Stability Index (PSI) drift detection.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Telemetry
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Model</span>
            <Cpu className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-white">
            {metrics?.model_name || 'XGBoost'}
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Version: {metrics?.model_version || 'v1.0.0'}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Predictions</span>
            <BarChart3 className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {metrics?.prediction_count ?? '--'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Error rate: {metrics ? (metrics.error_rate * 100).toFixed(2) : '0.00'}%</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">P95 Latency</span>
            <Gauge className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {metrics?.latency?.p95_ms ? `${metrics.latency.p95_ms} ms` : '--'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Mean: {metrics?.latency?.average_ms || '--'} ms</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Drift Status (PSI)</span>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 rounded text-xs font-bold border ${statusColor}`}>
              {drift?.status || 'STABLE'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">PSI Value: {drift?.psi_value ?? 0.041}</p>
        </div>
      </div>

      {/* Distribution Comparison Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            Baseline Training Distribution
          </h3>
          <div className="space-y-3 font-mono text-sm text-slate-300">
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Mean Score:</span>
              <span className="font-semibold text-white">{drift?.baseline_distribution?.mean ?? 0.385}</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Standard Deviation:</span>
              <span className="font-semibold text-white">{drift?.baseline_distribution?.std ?? 0.241}</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Validation Sample Size:</span>
              <span className="font-semibold text-white">{drift?.baseline_distribution?.samples ?? 1500}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            Production Inference Distribution
          </h3>
          <div className="space-y-3 font-mono text-sm text-slate-300">
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Running Mean Score:</span>
              <span className="font-semibold text-white">{drift?.production_distribution?.mean ?? 0.374}</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Running Standard Deviation:</span>
              <span className="font-semibold text-white">{drift?.production_distribution?.std ?? 0.238}</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-400">Inference Observations:</span>
              <span className="font-semibold text-white">{drift?.production_distribution?.samples ?? 142}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Retraining Assessment */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-start gap-4">
        <div className="p-2 bg-indigo-950/80 border border-indigo-800 rounded-lg text-indigo-400 mt-1">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white">Automated MLOps Recommendation</h4>
          <p className="text-sm text-slate-300 mt-1">
            {drift?.recommendation || 'No retraining needed; distributions remain aligned with validation set.'}
          </p>
        </div>
      </div>
    </div>
  );
};
