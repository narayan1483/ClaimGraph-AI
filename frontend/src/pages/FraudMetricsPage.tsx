/**
 * ClaimGraph AI — ML Model Benchmarks & Fraud Intelligence Lab.
 * Real metrics comparison across Logistic Regression, Random Forest, and XGBoost with live simulator.
 */

import React, { useState, useEffect } from 'react';
import { fraudService, type ModelMetricsComparison, type FraudPredictionResult } from '@/services/fraud';

export const FraudMetricsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetricsComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Simulator state
  const [simFeatures, setSimFeatures] = useState({
    claim_amount: 1850.0,
    previous_claim_count: 3,
    claims_last_30_days: 2,
    average_claim_amount: 800.0,
    amount_deviation: 1050.0,
    amount_to_msrp_ratio: 1.45,
    device_claim_count: 2,
    customer_claim_frequency: 0.65,
    location_frequency: 5,
    repair_shop_frequency: 4,
    days_since_last_claim: 14.0,
    device_age: 180,
  });

  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<FraudPredictionResult | null>(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fraudService.getModelMetrics();
      setMetrics(data);
    } catch (err: any) {
      console.error('Failed to load metrics', err);
      setError(err?.response?.data?.message || err?.message || 'Failed to load model metrics.');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSimulating(true);
      const res = await fraudService.predictFraud(simFeatures);
      setSimResult(res);
    } catch (err: any) {
      console.error('Simulation failed', err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="pb-4 border-b border-[#162032] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></span>
            <h1 className="text-xl font-bold tracking-tight text-slate-100 font-sans">
              ML Model Benchmark & Evaluation Matrix
            </h1>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Empirical validation results across Logistic Regression, Random Forest, and XGBoost on 6,000 synthetic insurance claims
          </p>
        </div>
        <button
          onClick={loadMetrics}
          className="px-3 py-1.5 text-xs font-mono text-slate-300 hover:text-white bg-[#0f172a] hover:bg-[#1e293b] border border-[#1e293b] rounded-lg transition-colors flex items-center gap-1.5 self-start sm:self-auto"
        >
          <span>Refresh Benchmark Telemetry</span>
        </button>
      </div>

      {error && (
        <div className="p-3 text-xs bg-rose-950/60 border border-rose-800 text-rose-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Model Benchmark Table */}
      <div className="bg-[#090d16] border border-[#162032] rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 bg-[#0d1322] border-b border-[#162032] flex items-center justify-between">
          <h2 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold flex items-center gap-2">
            <span>Model Validation Performance Comparison</span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
              Selected: Random Forest (F1: 0.9633)
            </span>
          </h2>
          <span className="text-[11px] font-mono text-slate-500">Stratified 80/20 Holdout Split</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#0a0f1d] border-b border-[#162032] text-slate-400 uppercase text-[11px]">
              <tr>
                <th className="px-4 py-3">Classifier Model</th>
                <th className="px-4 py-3">Precision</th>
                <th className="px-4 py-3">Recall</th>
                <th className="px-4 py-3">F1-Score</th>
                <th className="px-4 py-3">ROC-AUC</th>
                <th className="px-4 py-3">PR-AUC</th>
                <th className="px-4 py-3">Selection Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#131c2e]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    Loading benchmark metrics...
                  </td>
                </tr>
              ) : metrics?.benchmark_results ? (
                Object.entries(metrics.benchmark_results).map(([modelName, stats]) => {
                  const isWinner = modelName === metrics.best_model;
                  return (
                    <tr
                      key={modelName}
                      className={isWinner ? 'bg-cyan-950/20 border-l-2 border-cyan-400' : 'hover:bg-[#0f172a]/40'}
                    >
                      <td className="px-4 py-3.5 font-bold text-slate-200">
                        {modelName}
                        {isWinner && (
                          <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-cyan-500 text-slate-950 font-bold uppercase tracking-wider">
                            Winner
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-slate-300">
                        {(stats.precision * 100).toFixed(2)}%
                      </td>
                      <td className="px-4 py-3.5 text-slate-300">
                        {(stats.recall * 100).toFixed(2)}%
                      </td>
                      <td className="px-4 py-3.5 font-bold text-cyan-300">
                        {stats.f1_score.toFixed(4)}
                      </td>
                      <td className="px-4 py-3.5 text-emerald-400 font-bold">
                        {stats.roc_auc.toFixed(4)}
                      </td>
                      <td className="px-4 py-3.5 text-emerald-400 font-bold">
                        {stats.pr_auc.toFixed(4)}
                      </td>
                      <td className="px-4 py-3.5">
                        {isWinner ? (
                          <span className="text-emerald-400 text-[11px] font-bold">
                            Selected for Production Inference
                          </span>
                        ) : (
                          <span className="text-slate-500 text-[11px]">Benchmarked Baseline</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interactive ML Simulator & Feature Attribution Sandbox */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Simulator Form (7 cols) */}
        <div className="lg:col-span-7 bg-[#090d16] border border-[#162032] rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#162032]">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              Live ML Feature Vector Simulation Sandbox
            </h2>
            <span className="text-[10px] font-mono text-slate-500">POST /api/v1/fraud/predict</span>
          </div>

          <form onSubmit={handleSimulate} className="space-y-4 font-mono text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">claim_amount ($)</label>
                <input
                  type="number"
                  value={simFeatures.claim_amount}
                  onChange={(e) => setSimFeatures({ ...simFeatures, claim_amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">previous_claim_count</label>
                <input
                  type="number"
                  value={simFeatures.previous_claim_count}
                  onChange={(e) => setSimFeatures({ ...simFeatures, previous_claim_count: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">claims_last_30_days</label>
                <input
                  type="number"
                  value={simFeatures.claims_last_30_days}
                  onChange={(e) => setSimFeatures({ ...simFeatures, claims_last_30_days: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">average_claim_amount</label>
                <input
                  type="number"
                  value={simFeatures.average_claim_amount}
                  onChange={(e) => setSimFeatures({ ...simFeatures, average_claim_amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">amount_to_msrp_ratio</label>
                <input
                  type="number"
                  step="0.05"
                  value={simFeatures.amount_to_msrp_ratio}
                  onChange={(e) => setSimFeatures({ ...simFeatures, amount_to_msrp_ratio: parseFloat(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">repair_shop_frequency</label>
                <input
                  type="number"
                  value={simFeatures.repair_shop_frequency}
                  onChange={(e) => setSimFeatures({ ...simFeatures, repair_shop_frequency: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 bg-[#0c1220] border border-[#162032] rounded text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={simulating}
                className="px-4 py-2 font-mono text-xs uppercase tracking-wider bg-gradient-to-r from-cyan-400 to-teal-400 hover:from-cyan-300 hover:to-teal-300 text-slate-950 font-bold rounded-lg shadow-lg shadow-cyan-950/40 transition-all flex items-center gap-2"
              >
                {simulating ? 'Calculating Inference...' : 'Execute ML Model Prediction'}
              </button>
            </div>
          </form>
        </div>

        {/* Simulator Results & SHAP factors (5 cols) */}
        <div className="lg:col-span-5 bg-[#090d16] border border-[#162032] rounded-xl p-5 shadow-xl">
          <h2 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold mb-4 pb-2 border-b border-[#162032]">
            Inference Telemetry Output
          </h2>

          {!simResult ? (
            <div className="p-8 text-center bg-[#070b14] border border-[#162032] rounded-lg text-slate-500 font-mono text-xs">
              Execute prediction to view live probability and SHAP attribution.
            </div>
          ) : (
            <div className="space-y-4 font-mono text-xs">
              <div className="p-4 bg-[#0c1220] border border-[#162032] rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Fraud Probability:</span>
                  <span
                    className={`text-2xl font-bold ${
                      simResult.fraud_probability >= 0.75
                        ? 'text-rose-400'
                        : simResult.fraud_probability >= 0.5
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {(simResult.fraud_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Assigned Risk Level:</span>
                  <span
                    className={`px-2 py-0.5 rounded font-bold ${
                      simResult.risk_level === 'CRITICAL'
                        ? 'bg-rose-950 text-rose-300 border border-rose-800'
                        : simResult.risk_level === 'HIGH'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {simResult.risk_level}
                  </span>
                </div>
              </div>

              <div>
                <h3 className="text-[11px] text-slate-400 uppercase tracking-wider mb-2 font-semibold">
                  Top SHAP Risk Factors:
                </h3>
                <div className="space-y-2">
                  {simResult.top_factors.map((factor, idx) => (
                    <div key={idx} className="p-2.5 bg-[#0b101c] border border-[#162032] rounded-lg">
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-200">{factor.feature}</span>
                        <span
                          className={`font-bold ${
                            factor.impact > 0 ? 'text-rose-400' : 'text-emerald-400'
                          }`}
                        >
                          {factor.impact > 0 ? `+${factor.impact.toFixed(3)}` : factor.impact.toFixed(3)}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 font-sans mt-0.5">{factor.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
