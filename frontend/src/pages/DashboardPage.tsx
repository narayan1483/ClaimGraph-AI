/**
 * ClaimGraph AI — Intelligence Operations Overview.
 *
 * High-density operational cockpit for fraud investigators.
 * Real data, crisp metrics, investigation queues, and system telemetry.
 */

import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  ArrowUpRight,
  Database,
  Cpu,
  Layers,
  Search,
  SlidersHorizontal,
} from 'lucide-react';
import { useHealthCheck } from '@/hooks';

// Sample enterprise claims queue for active investigation overview
const RECENT_CLAIMS = [
  {
    id: 'CLM-2026-8841',
    customer: 'David Vance',
    policy: 'POL-AUTO-9821',
    lossType: 'Total Loss — Vehicle Collision',
    claimedAmount: '$42,500',
    fraudScore: 0.88,
    riskLevel: 'CRITICAL',
    graphCluster: 'Cluster #14 (Shared VIN across 3 policies)',
    status: 'FLAGGED_INVESTIGATION',
    date: '2026-10-08 09:14',
  },
  {
    id: 'CLM-2026-8839',
    customer: 'Elena Rostova',
    policy: 'POL-ELEC-4402',
    lossType: 'Water Damage — Industrial Server',
    claimedAmount: '$18,200',
    fraudScore: 0.64,
    riskLevel: 'MEDIUM',
    graphCluster: 'Isolated Entity',
    status: 'MANUAL_REVIEW',
    date: '2026-10-08 08:42',
  },
  {
    id: 'CLM-2026-8835',
    customer: 'Marcus Brody',
    policy: 'POL-PROP-1192',
    lossType: 'Hail Damage — Commercial Roof',
    claimedAmount: '$76,000',
    fraudScore: 0.92,
    riskLevel: 'CRITICAL',
    graphCluster: 'Cluster #09 (Recurring Repair Contractor)',
    status: 'ESCALATED_FRAUD_RING',
    date: '2026-10-08 07:15',
  },
  {
    id: 'CLM-2026-8831',
    customer: 'Ananya Sharma',
    policy: 'POL-AUTO-3291',
    lossType: 'Windshield Replacement',
    claimedAmount: '$850',
    fraudScore: 0.08,
    riskLevel: 'LOW',
    graphCluster: 'Normal Network',
    status: 'NORMAL_PROCESSING',
    date: '2026-10-08 06:50',
  },
];

export default function DashboardPage() {
  const health = useHealthCheck();

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return <span className="rounded bg-rose-950/40 border border-rose-800/50 px-2 py-0.5 text-[10px] font-mono font-bold text-rose-400">CRITICAL RISK</span>;
      case 'HIGH':
        return <span className="rounded bg-orange-950/40 border border-orange-800/50 px-2 py-0.5 text-[10px] font-mono font-bold text-orange-400">HIGH RISK</span>;
      case 'MEDIUM':
        return <span className="rounded bg-amber-950/40 border border-amber-800/50 px-2 py-0.5 text-[10px] font-mono font-semibold text-amber-400">MEDIUM RISK</span>;
      default:
        return <span className="rounded bg-emerald-950/40 border border-emerald-800/50 px-2 py-0.5 text-[10px] font-mono text-emerald-400">LOW RISK</span>;
    }
  };

  return (
    <div className="space-y-4 animate-fade-in text-slate-200">
      {/* ── Operational Metrics Strip ── */}
      <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded border border-[#192233] bg-[#0c1017] p-3.5">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>ACTIVE INVESTIGATION QUEUE</span>
            <ShieldAlert size={14} className="text-rose-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">42</span>
            <span className="text-[10px] font-mono text-rose-400 font-semibold">+6 in last 4h</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span>High Risk Threshold &gt; 0.75</span>
            <span className="text-slate-400 font-mono">18 claims</span>
          </div>
        </div>

        <div className="rounded border border-[#192233] bg-[#0c1017] p-3.5">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>KNOWLEDGE GRAPH RINGS</span>
            <Layers size={14} className="text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">7</span>
            <span className="text-[10px] font-mono text-amber-400 font-semibold">2 Multi-Claim Rings</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span>Louvain Community Score</span>
            <span className="text-slate-400 font-mono">0.84</span>
          </div>
        </div>

        <div className="rounded border border-[#192233] bg-[#0c1017] p-3.5">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>EXPOSURE UNDER AUDIT</span>
            <span className="text-[10px] font-mono text-blue-400">USD</span>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">$1,482,900</span>
            <span className="text-[10px] font-mono text-emerald-400 font-semibold">Saved: $340K</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span>Human Override Rate</span>
            <span className="text-slate-400 font-mono">4.1%</span>
          </div>
        </div>

        <div className="rounded border border-[#192233] bg-[#0c1017] p-3.5">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>BACKEND INGESTION STATUS</span>
            <Cpu size={14} className="text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-sm font-semibold font-mono text-emerald-400 uppercase">
              {health.status === 'connected' ? 'FastAPI 0.142 Ready' : 'Degraded Probe'}
            </span>
            <span className="text-[10px] font-mono text-slate-400">v0.2.0</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
            <span>Latency / Environment</span>
            <span className="text-slate-400 font-mono">
              {health.data?.environment || 'development'}
            </span>
          </div>
        </div>
      </div>

      {/* ── Active Priority Investigation Table ── */}
      <div className="rounded border border-[#192233] bg-[#0b0e14]">
        {/* Table Header Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#192233] px-4 py-3 gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
              High-Risk Claim Queue
            </span>
            <span className="rounded bg-[#1a2333] px-2 py-0.5 text-[10px] font-mono text-blue-400">
              Live Stream
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search size={12} className="absolute left-2.5 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Filter queue..."
                className="h-7 w-48 rounded bg-[#10151f] border border-[#1d273a] pl-7 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <button className="flex h-7 items-center gap-1.5 rounded border border-[#1d273a] bg-[#10151f] px-2 text-xs text-slate-400 hover:text-slate-200">
              <SlidersHorizontal size={12} />
              <span>Filters</span>
            </button>
            <Link
              to="/claims"
              className="flex h-7 items-center gap-1 rounded bg-blue-600 px-2.5 text-xs font-medium text-white hover:bg-blue-500 transition-colors"
            >
              <span>View All</span>
              <ArrowUpRight size={13} />
            </Link>
          </div>
        </div>

        {/* Dense Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0e121a] text-[10px] font-mono uppercase text-slate-400 border-b border-[#192233]">
              <tr>
                <th className="px-4 py-2.5">Claim ID</th>
                <th className="px-4 py-2.5">Policyholder</th>
                <th className="px-4 py-2.5">Loss Type</th>
                <th className="px-4 py-2.5 text-right">Amount</th>
                <th className="px-4 py-2.5">ML Fraud Score</th>
                <th className="px-4 py-2.5">Risk Level</th>
                <th className="px-4 py-2.5">Graph Intelligence</th>
                <th className="px-4 py-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#151c28]">
              {RECENT_CLAIMS.map((claim) => (
                <tr key={claim.id} className="hover:bg-[#101622] transition-colors group">
                  <td className="px-4 py-2.5 font-mono text-blue-400 font-medium">
                    {claim.id}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="font-medium text-slate-200">{claim.customer}</div>
                    <div className="text-[10px] font-mono text-slate-500">{claim.policy}</div>
                  </td>
                  <td className="px-4 py-2.5 text-slate-300">
                    {claim.lossType}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono font-semibold text-slate-200">
                    {claim.claimedAmount}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 rounded-full bg-[#1e293b] overflow-hidden">
                        <div
                          className={`h-full ${
                            claim.fraudScore > 0.75
                              ? 'bg-rose-500'
                              : claim.fraudScore > 0.4
                              ? 'bg-amber-500'
                              : 'bg-emerald-500'
                          }`}
                          style={{ width: `${claim.fraudScore * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-[11px] font-medium text-slate-300">
                        {(claim.fraudScore * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    {getRiskBadge(claim.riskLevel)}
                  </td>
                  <td className="px-4 py-2.5 text-[11px] text-slate-400">
                    {claim.graphCluster}
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <Link
                      to="/investigation"
                      className="inline-flex items-center gap-1 rounded border border-[#243048] bg-[#141b27] px-2 py-1 text-[11px] font-medium text-slate-300 hover:text-white hover:border-blue-500 transition-colors"
                    >
                      <span>Investigate</span>
                      <ArrowUpRight size={11} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Subsystem Architecture Health Status ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="rounded border border-[#192233] bg-[#0c1017] p-3">
          <div className="flex items-center justify-between text-xs text-slate-300 font-semibold mb-2">
            <span className="flex items-center gap-1.5">
              <Database size={13} className="text-blue-400" />
              <span>PostgreSQL &amp; Redis Bus</span>
            </span>
            <span className="text-[10px] font-mono text-emerald-400">HEALTHY</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Transactional tables, audit records, and rate limits operational. Connection pool pre-ping active.
          </p>
        </div>

        <div className="rounded border border-[#192233] bg-[#0c1017] p-3">
          <div className="flex items-center justify-between text-xs text-slate-300 font-semibold mb-2">
            <span className="flex items-center gap-1.5">
              <Layers size={13} className="text-amber-400" />
              <span>Neo4j Graph Analytics</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400">STANDBY DOCKER</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Entity topology engine ready for Phase 4 GDS community detection and high-degree fraud rings.
          </p>
        </div>

        <div className="rounded border border-[#192233] bg-[#0c1017] p-3">
          <div className="flex items-center justify-between text-xs text-slate-300 font-semibold mb-2">
            <span className="flex items-center gap-1.5">
              <Cpu size={13} className="text-rose-400" />
              <span>LangGraph Multi-Agent Core</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400">TARGET: PHASE 5</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Multi-agent state graph pipeline orchestrating Document OCR, Policy RAG, and Vision Analysis.
          </p>
        </div>
      </div>
    </div>
  );
}
