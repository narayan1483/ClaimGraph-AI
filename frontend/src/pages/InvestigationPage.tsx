/**
 * ClaimGraph AI — Autonomous Investigation Workspace & Adjudication Desk.
 *
 * Professional enterprise fraud intelligence interface connecting:
 * - Real claim metadata & telemetry
 * - Live Neo4j Knowledge Graph interactive visualization
 * - LangGraph 8-Agent reasoning execution trace
 * - Categorized evidence matrix (FACT, ML SIGNAL, GRAPH SIGNAL, AI ANALYSIS, RECOMMENDATION)
 * - Complete synthesized investigation dossier
 * - Mandatory Human Investigator Decision controls (APPROVE, REJECT, ESCALATE, REQUEST_MORE_INFO)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  investigationService,
  type InvestigationRunResponse,
  type GraphDataResponse,
  type GraphRiskResult,
  type RAGQueryResponse,
} from '@/services/investigation';
import { claimsService, type ClaimDetailItem } from '@/services/claims';
import { InteractiveKnowledgeGraph } from '@/components/InteractiveKnowledgeGraph';
import {
  ShieldAlert,
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  FileText,
  Cpu,
  Share2,
  BookOpen,
  Search,
  Layers,
} from 'lucide-react';

export const InvestigationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const claimIdParam = searchParams.get('claim_id') || 'CLM-2026-0001';

  const [claimIdInput, setClaimIdInput] = useState(claimIdParam);
  const [claim, setClaim] = useState<ClaimDetailItem | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationRunResponse | null>(null);
  const [graphData, setGraphData] = useState<GraphDataResponse | null>(null);
  const [graphRisk, setGraphRisk] = useState<GraphRiskResult | null>(null);

  const [loadingClaim, setLoadingClaim] = useState(false);
  const [runningInvestigation, setRunningInvestigation] = useState(false);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Adjudication modal state
  const [adjudicationDecision, setAdjudicationDecision] = useState<'APPROVE' | 'REJECT' | 'ESCALATE' | 'REQUEST_MORE_INFO' | null>(null);
  const [adjudicationNotes, setAdjudicationNotes] = useState('');
  const [badgeNumber, setBadgeNumber] = useState('INV-LEAD-NARAYAN');
  const [submittingDecision, setSubmittingDecision] = useState(false);

  // Active view tab in workspace
  const [activeTab, setActiveTab] = useState<'overview' | 'graph' | 'agents' | 'report' | 'policy'>('overview');

  // Policy query state
  const [policyQuery, setPolicyQuery] = useState('What documentation is mandatory for screen damage claims?');
  const [policyResponse, setPolicyResponse] = useState<RAGQueryResponse | null>(null);
  const [queryingPolicy, setQueryingPolicy] = useState(false);

  // Load claim and existing investigation
  const loadClaimAndInvestigation = useCallback(async (targetId: string) => {
    if (!targetId) return;
    try {
      setLoadingClaim(true);
      setError(null);

      // Fetch claim
      const claimData = await claimsService.getClaim(targetId);
      setClaim(claimData);

      // Fetch existing investigation if already executed
      try {
        const existingInv = await investigationService.getInvestigation(targetId);
        setInvestigation(existingInv);
      } catch {
        setInvestigation(null);
      }

      // Fetch graph data
      setLoadingGraph(true);
      try {
        const [gData, gRisk] = await Promise.all([
          investigationService.getClaimGraph(targetId),
          investigationService.getGraphRisk(targetId),
        ]);
        setGraphData(gData);
        setGraphRisk(gRisk);
      } catch (gErr) {
        console.warn('Graph data fetch notice:', gErr);
      } finally {
        setLoadingGraph(false);
      }
    } catch (err: any) {
      console.error('Failed to load claim data', err);
      setError(err?.response?.data?.message || err?.message || `Claim '${targetId}' could not be loaded.`);
    } finally {
      setLoadingClaim(false);
    }
  }, []);

  useEffect(() => {
    if (claimIdParam) {
      setClaimIdInput(claimIdParam);
      loadClaimAndInvestigation(claimIdParam);
    }
  }, [claimIdParam, loadClaimAndInvestigation]);

  // Execute full LangGraph multi-agent investigation
  const handleRunInvestigation = async () => {
    if (!claim) return;
    try {
      setRunningInvestigation(true);
      setError(null);
      setSuccessMessage(null);

      const targetId = claim.claim_id || claim.id;
      const result = await investigationService.runInvestigation(targetId);
      setInvestigation(result);
      setSuccessMessage(`AI multi-agent investigation completed for #${targetId}.`);

      // Refresh graph data and claim
      const [gData, gRisk, refreshedClaim] = await Promise.all([
        investigationService.getClaimGraph(targetId),
        investigationService.getGraphRisk(targetId),
        claimsService.getClaim(targetId),
      ]);
      setGraphData(gData);
      setGraphRisk(gRisk);
      setClaim(refreshedClaim);
    } catch (err: any) {
      console.error('Investigation failed', err);
      setError(err?.response?.data?.detail || err?.message || 'Investigation execution failed.');
    } finally {
      setRunningInvestigation(false);
    }
  };

  // Submit human investigator adjudication
  const handleConfirmDecision = async () => {
    if (!investigation || !adjudicationDecision) return;
    try {
      setSubmittingDecision(true);
      setError(null);

      const resp = await investigationService.recordDecision(
        investigation.investigation_id,
        adjudicationDecision,
        adjudicationNotes,
        badgeNumber
      );

      setSuccessMessage(`Adjudication confirmed: ${resp.decision}. Claim status updated to ${resp.new_claim_status}.`);
      setAdjudicationDecision(null);
      setAdjudicationNotes('');

      // Refresh claim
      if (claim) {
        const refreshed = await claimsService.getClaim(claim.claim_id || claim.id);
        setClaim(refreshed);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Adjudication submission failed.');
    } finally {
      setSubmittingDecision(false);
    }
  };

  // Handle RAG Policy query
  const handleQueryPolicy = async () => {
    if (!policyQuery.trim()) return;
    try {
      setQueryingPolicy(true);
      const resp = await investigationService.queryPolicy(policyQuery, claim?.claim_id);
      setPolicyResponse(resp);
    } catch (err: any) {
      console.error('Policy RAG query failed', err);
    } finally {
      setQueryingPolicy(false);
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'HIGH':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'MEDIUM':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* ── Top Bar: Search Claim & Actions ───────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              Phase 4 Core AI Engine
            </span>
            <span className="text-slate-500 text-xs font-mono">LangGraph · Neo4j · Deterministic Hybrid Risk</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">Autonomous Claim Investigation Workspace</h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={claimIdInput}
              onChange={(e) => setClaimIdInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadClaimAndInvestigation(claimIdInput)}
              placeholder="Search Claim ID..."
              className="pl-9 pr-3 py-1.5 bg-slate-900 border border-white/10 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            onClick={() => loadClaimAndInvestigation(claimIdInput)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-white/10 transition-colors"
          >
            Load
          </button>
          <button
            onClick={handleRunInvestigation}
            disabled={runningInvestigation || !claim}
            className="flex items-center gap-2 px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-md transition-all shadow-cyan-950"
          >
            {runningInvestigation ? (
              <>
                <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                <span>Executing 8 Agents...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                <span>Run AI Investigation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── Status Banners ────────────────────────────────────────── */}
      {loadingClaim && (
        <div className="flex items-center justify-center p-6 font-mono text-xs text-slate-400 border border-white/5 bg-slate-900/40 rounded-xl">
          <RotateCcw className="w-4 h-4 animate-spin text-cyan-400 mr-2" />
          <span>Retrieving claim metadata and historical telemetry...</span>
        </div>
      )}
      {error && (

        <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-white">✕</button>
        </div>
      )}
      {successMessage && (
        <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* ── SECTION 1: CLAIM PROFILE & REAL AI RISK RIBBON ─────────── */}
      {claim && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Claim Metadata Card */}
          <div className="lg:col-span-1 bg-slate-900/60 border border-white/10 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Claim Subject</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-slate-300">
                {claim.status}
              </span>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white font-mono">{claim.claim_id}</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {claim.customer?.user?.full_name || 'Policyholder'} · {claim.customer?.user?.email || 'user@domain.com'}
              </p>
            </div>
            <div className="space-y-1.5 text-xs font-mono border-t border-white/5 pt-2.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Asset:</span>
                <span className="text-slate-300 truncate max-w-[150px]">{claim.device?.product?.name || 'Device'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Serial #:</span>
                <span className="text-slate-300">{claim.device?.serial_number || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Claim Amount:</span>
                <span className="text-cyan-400 font-semibold">${Number(claim.claim_amount).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Jurisdiction:</span>
                <span className="text-slate-300">{claim.location}</span>
              </div>
            </div>
            <div className="border-t border-white/5 pt-2">
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Description</span>
              <p className="text-xs text-slate-300 line-clamp-3 italic">"{claim.description}"</p>
            </div>
          </div>

          {/* AI Risk Intelligence Header (4 metrics + Score Breakdown) */}
          <div className="lg:col-span-3 bg-slate-900/60 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  Deterministic Hybrid Risk Engine Output
                </span>
                {investigation && (
                  <span className="text-[10px] font-mono text-slate-500">
                    ID: {investigation.investigation_id}
                  </span>
                )}
              </div>

              {/* 4 Score Tiles */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {/* 1. ML Fraud Probability */}
                <div className="bg-slate-950/60 border border-white/5 rounded-lg p-3">
                  <span className="text-[10px] font-mono text-slate-400 block mb-1">ML Fraud Score</span>
                  <div className="text-2xl font-bold font-mono text-purple-400">
                    {investigation
                      ? `${(investigation.fraud_score * 100).toFixed(1)}%`
                      : claim.fraud_probability !== null
                      ? `${(Number(claim.fraud_probability) * 100).toFixed(1)}%`
                      : '—'}
                  </div>
                  <span className="text-[9px] font-mono text-slate-500 block mt-1">XGBoost Ensemble</span>
                </div>

                {/* 2. Graph Risk Score */}
                <div className="bg-slate-950/60 border border-white/5 rounded-lg p-3">
                  <span className="text-[10px] font-mono text-slate-400 block mb-1">Knowledge Graph</span>
                  <div className="text-2xl font-bold font-mono text-amber-400">
                    {investigation
                      ? `${(investigation.graph_score * 100).toFixed(1)}%`
                      : graphRisk
                      ? `${(graphRisk.graph_risk_score * 100).toFixed(1)}%`
                      : '—'}
                  </div>
                  <span className="text-[9px] font-mono text-slate-500 block mt-1">
                    {graphRisk ? `${graphRisk.degree} Links · ${graphRisk.connected_cluster_size} Nodes` : 'Neo4j Topology'}
                  </span>
                </div>

                {/* 3. Final Composite Risk */}
                <div className="bg-slate-950/60 border border-white/5 rounded-lg p-3">
                  <span className="text-[10px] font-mono text-slate-400 block mb-1">Final Risk Score</span>
                  <div className="text-2xl font-bold font-mono text-cyan-400">
                    {investigation ? `${(investigation.final_risk_score * 100).toFixed(0)} / 100` : '—'}
                  </div>
                  <span className="text-[9px] font-mono text-slate-500 block mt-1">Deterministic Formula</span>
                </div>

                {/* 4. Risk Level & Action */}
                <div className="bg-slate-950/60 border border-white/5 rounded-lg p-3">
                  <span className="text-[10px] font-mono text-slate-400 block mb-1">Risk Classification</span>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-mono font-bold border ${getRiskBadgeColor(
                        investigation?.risk_level || claim.risk_level || 'LOW'
                      )}`}
                    >
                      {investigation?.risk_level || claim.risk_level || 'PENDING'}
                    </span>
                  </div>
                  <span className="text-[9px] font-mono text-slate-400 block mt-1 truncate">
                    {investigation?.recommendation?.replace('_', ' ') || 'Awaiting Run'}
                  </span>
                </div>
              </div>
            </div>

            {/* Score Breakdown Bar */}
            {investigation?.score_breakdown && (
              <div className="mt-4 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1.5">
                  <span>Weight Contributions:</span>
                  <span className="text-slate-500">ML: 30% · Graph: 25% · Doc: 15% · Vision: 10% · Policy: 10% · Velocity: 10%</span>
                </div>
                <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex">
                  <div
                    style={{ width: `${(investigation.score_breakdown.ml_fraud_component || 0) * 100}%` }}
                    className="bg-purple-500"
                    title="ML Component"
                  />
                  <div
                    style={{ width: `${(investigation.score_breakdown.graph_risk_component || 0) * 100}%` }}
                    className="bg-amber-500"
                    title="Graph Component"
                  />
                  <div
                    style={{ width: `${(investigation.score_breakdown.document_inconsistency_component || 0) * 100}%` }}
                    className="bg-rose-500"
                    title="Document Component"
                  />
                  <div
                    style={{ width: `${(investigation.score_breakdown.vision_evidence_component || 0) * 100}%` }}
                    className="bg-sky-500"
                    title="Vision Component"
                  />
                  <div
                    style={{ width: `${(investigation.score_breakdown.policy_compliance_component || 0) * 100}%` }}
                    className="bg-emerald-500"
                    title="Policy Component"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── SECTION 2: WORKSPACE NAVIGATION TABS ──────────────────── */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-2 overflow-x-auto text-xs font-mono">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'overview' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Evidence & Categorization</span>
        </button>
        <button
          onClick={() => setActiveTab('graph')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'graph' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Share2 className="w-3.5 h-3.5" />
          <span>Knowledge Graph ({graphData?.node_count || 0} Nodes)</span>
        </button>
        <button
          onClick={() => setActiveTab('agents')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'agents' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>8-Agent Execution Trace</span>
        </button>
        <button
          onClick={() => setActiveTab('report')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'report' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Investigation Dossier</span>
        </button>
        <button
          onClick={() => setActiveTab('policy')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'policy' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>RAG Policy Assistant</span>
        </button>
      </div>

      {/* ── TAB 1: EVIDENCE & CATEGORIZATION MATRIX ────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Categorized Fraud Evidence Matrix</h3>
            <span className="text-xs font-mono text-slate-500">
              Clear attribution: FACT · ML SIGNAL · GRAPH SIGNAL · AI ANALYSIS · RECOMMENDATION
            </span>
          </div>

          {investigation?.evidence && investigation.evidence.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {investigation.evidence.map((ev, i) => {
                const badgeStyle =
                  ev.category === 'FACT'
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-400'
                    : ev.category === 'ML SIGNAL'
                    ? 'border-purple-500/30 bg-purple-500/10 text-purple-400'
                    : ev.category === 'GRAPH SIGNAL'
                    ? 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                    : ev.category === 'AI ANALYSIS'
                    ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400'
                    : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400';

                return (
                  <div key={i} className="bg-slate-900/60 border border-white/10 rounded-xl p-4 flex flex-col justify-between space-y-2">
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold border ${badgeStyle}`}>
                          {ev.category}
                        </span>
                        {ev.weight !== undefined && (
                          <span className="text-[10px] font-mono text-slate-400">Impact: +{ev.weight}</span>
                        )}
                      </div>
                      <p className="text-xs text-slate-200 leading-relaxed">{ev.text}</p>
                    </div>
                    {ev.source && (
                      <span className="text-[10px] font-mono text-slate-500 pt-1 border-t border-white/5 block">
                        Source: {ev.source}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-white/10 rounded-xl p-8 text-center text-slate-500 font-mono text-xs">
              <ShieldAlert className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <span>No evidence generated yet. Click "Run AI Investigation" above to execute multi-agent analysis.</span>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: KNOWLEDGE GRAPH INTERACTIVE VISUALIZATION ───────── */}
      {activeTab === 'graph' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">Interactive Neo4j Knowledge Graph</h3>
              <p className="text-xs text-slate-400">Click any entity to inspect attributes and connections.</p>
            </div>
            {graphRisk && (
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-slate-400">
                  Shared Device:{' '}
                  <strong className={graphRisk.shared_device_detected ? 'text-rose-400' : 'text-emerald-400'}>
                    {graphRisk.shared_device_detected ? 'YES (COLLUSION)' : 'NO'}
                  </strong>
                </span>
                <span className="text-slate-400">
                  Suspicious Shop:{' '}
                  <strong className={graphRisk.suspicious_repair_shop_detected ? 'text-rose-400' : 'text-emerald-400'}>
                    {graphRisk.suspicious_repair_shop_detected ? 'FLAGGED' : 'CLEAR'}
                  </strong>
                </span>
              </div>
            )}
          </div>

          <InteractiveKnowledgeGraph data={graphData} loading={loadingGraph} />

          {/* Graph Evidence Statements */}
          {graphRisk?.evidence && graphRisk.evidence.length > 0 && (
            <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
              <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">Graph Analytics Findings</h4>
              <ul className="space-y-1.5 text-xs text-slate-300 font-mono">
                {graphRisk.evidence.map((stmt, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-400">•</span>
                    <span>{stmt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: 8-AGENT EXECUTION TRACE ─────────────────────────── */}
      {activeTab === 'agents' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">LangGraph Multi-Agent Orchestration Sequence</h3>
            <span className="text-xs font-mono text-cyan-400">8 / 8 Specialized Agents</span>
          </div>

          {investigation?.agent_results ? (
            <div className="space-y-3">
              {Object.entries(investigation.agent_results).map(([agentName, agent], idx) => (
                <div key={agentName} className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-2.5 mb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 text-xs flex items-center justify-center font-mono font-bold">
                        {idx + 1}
                      </span>
                      <h4 className="font-semibold text-slate-100 text-sm">{agentName}</h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                        {agent.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                      <span>Confidence: {(agent.confidence * 100).toFixed(0)}%</span>
                      <span>·</span>
                      <span>Latency: {agent.latency_ms}ms</span>
                    </div>
                  </div>

                  {/* Evidence list */}
                  <div className="space-y-1 text-xs text-slate-300 mb-2">
                    {agent.evidence.map((ev, eIdx) => (
                      <p key={eIdx} className="flex items-start gap-2">
                        <span className="text-cyan-400 font-bold">›</span>
                        <span>{ev}</span>
                      </p>
                    ))}
                  </div>

                  <span className="text-[10px] font-mono text-slate-500 block pt-1 border-t border-white/5">
                    Source: {agent.source}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-white/10 rounded-xl p-8 text-center text-slate-500 font-mono text-xs">
              Run investigation to visualize execution telemetry and agent reasoning traces.
            </div>
          )}
        </div>
      )}

      {/* ── TAB 4: COMPLETE INVESTIGATION DOSSIER REPORT ───────────── */}
      {activeTab === 'report' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Synthesized Investigation Dossier</h3>
            {investigation && (
              <button
                onClick={() => navigator.clipboard.writeText(investigation.investigation_report)}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded font-mono border border-white/10"
              >
                Copy Markdown
              </button>
            )}
          </div>

          {investigation?.investigation_report ? (
            <div className="bg-slate-900/80 border border-white/10 rounded-xl p-6 prose prose-invert prose-sm max-w-none font-mono text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap">
              {investigation.investigation_report}
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-white/10 rounded-xl p-8 text-center text-slate-500 font-mono text-xs">
              No investigation report synthesized yet. Run investigation to generate report.
            </div>
          )}
        </div>
      )}

      {/* ── TAB 5: RAG POLICY ASSISTANT ────────────────────────────── */}
      {activeTab === 'policy' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Grounded Policy Knowledge Assistant (RAG)</h3>
            <p className="text-xs text-slate-400">
              Query official warranty policies, fraud guidelines, and escalation SOPs with exact textual citations.
            </p>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={policyQuery}
              onChange={(e) => setPolicyQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQueryPolicy()}
              placeholder="Ask a policy question (e.g., ADP deductible, 30-day reporting window, rapid claim red flags)..."
              className="flex-1 px-3 py-2 bg-slate-900 border border-white/10 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleQueryPolicy}
              disabled={queryingPolicy}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5"
            >
              {queryingPolicy ? <RotateCcw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              <span>Retrieve</span>
            </button>
          </div>

          {policyResponse && (
            <div className="bg-slate-900/70 border border-white/10 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-white/5 pb-2 text-xs font-mono">
                <span className="text-cyan-400 font-semibold">Grounded Answer</span>
                <span className="text-slate-500">
                  Latency: {policyResponse.latency_ms}ms · Tokens: {policyResponse.token_usage.total_tokens}
                </span>
              </div>
              <div className="text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                {policyResponse.answer}
              </div>

              {/* Retrieved Chunks */}
              <div className="border-t border-white/5 pt-2">
                <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1.5">
                  Retrieved Policy Provenance Chunks ({policyResponse.retrieved_chunks.length})
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {policyResponse.retrieved_chunks.map((chk) => (
                    <div key={chk.chunk_id} className="bg-slate-950/60 border border-white/5 rounded p-2.5 text-[11px] font-mono">
                      <div className="flex items-center justify-between text-slate-400 mb-1">
                        <strong className="text-slate-300">{chk.document}</strong>
                        <span>Score: {chk.similarity_score.toFixed(3)}</span>
                      </div>
                      <p className="text-slate-400 line-clamp-3">{chk.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── SECTION 3: HUMAN INVESTIGATOR DECISION ACTION BAR ──────── */}
      {claim && (
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-slate-950/95 border-t border-white/15 p-4 backdrop-blur-lg shadow-2xl">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-slate-300 font-medium">Human-in-the-Loop Governance Standard:</span>
              <span className="text-slate-400">Autonomous final denials strictly prohibited. Investigator signoff required.</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setAdjudicationDecision('APPROVE')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition-colors"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Approve</span>
              </button>
              <button
                onClick={() => setAdjudicationDecision('REJECT')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600/90 hover:bg-rose-500 text-white text-xs font-semibold shadow transition-colors"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => setAdjudicationDecision('ESCALATE')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-600/90 hover:bg-amber-500 text-white text-xs font-semibold shadow transition-colors"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Escalate to SIU</span>
              </button>
              <button
                onClick={() => setAdjudicationDecision('REQUEST_MORE_INFO')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-white/10 shadow transition-colors"
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Request Info</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── ADJUDICATION CONFIRMATION MODAL ───────────────────────── */}
      {adjudicationDecision && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-slate-900 border border-white/15 rounded-xl max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                <span>Confirm Decision:</span>
                <span className="text-cyan-400">{adjudicationDecision}</span>
              </h3>
              <button onClick={() => setAdjudicationDecision(null)} className="text-slate-400 hover:text-white text-xs">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-mono text-[11px] mb-1">Lead Investigator Badge #</label>
                <input
                  type="text"
                  value={badgeNumber}
                  onChange={(e) => setBadgeNumber(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-white/10 rounded text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-mono text-[11px] mb-1">Adjudication Rationale & Case Notes</label>
                <textarea
                  rows={3}
                  value={adjudicationNotes}
                  onChange={(e) => setAdjudicationNotes(e.target.value)}
                  placeholder="Document findings, phone interview observations, or proof of repair authorization..."
                  className="w-full px-3 py-1.5 bg-slate-950 border border-white/10 rounded text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 border-t border-white/10 pt-3">
              <button
                onClick={() => setAdjudicationDecision(null)}
                className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDecision}
                disabled={submittingDecision}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold rounded font-mono shadow"
              >
                {submittingDecision ? 'Recording Audit...' : 'Sign & Submit Adjudication'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
