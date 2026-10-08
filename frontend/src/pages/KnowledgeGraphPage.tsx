/**
 * ClaimGraph AI — Network Knowledge Graph Explorer Page.
 */

import React, { useState, useEffect } from 'react';
import { investigationService, type GraphDataResponse } from '@/services/investigation';
import { InteractiveKnowledgeGraph } from '@/components/InteractiveKnowledgeGraph';
import { Users, Cpu } from 'lucide-react';





export const KnowledgeGraphPage: React.FC = () => {
  const [claimId, setClaimId] = useState('CLM-2026-0001');
  const [graphData, setGraphData] = useState<GraphDataResponse | null>(null);
  const [clusters, setClusters] = useState<any[]>([]);
  const [sharedDevices, setSharedDevices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGraph = async (id: string) => {
    try {
      setLoading(true);
      const [gData, analytics] = await Promise.all([
        investigationService.getClaimGraph(id, 3),
        investigationService.getGraphClusters(),
      ]);
      setGraphData(gData);
      setClusters(analytics.clusters || []);
      setSharedDevices(analytics.shared_devices || []);
    } catch (e) {
      console.error('Failed to load graph', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph(claimId);
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-purple-500/10 text-purple-400 border border-purple-500/30">
              Neo4j Topology
            </span>
            <span className="text-slate-500 text-xs font-mono">Entity Resolution · Fraud Ring Discovery</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1">Knowledge Graph Intelligence</h1>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={claimId}
            onChange={(e) => setClaimId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchGraph(claimId)}
            placeholder="Claim ID..."
            className="px-3 py-1.5 bg-slate-900 border border-white/10 rounded-lg text-xs font-mono text-white placeholder-slate-500"
          />
          <button
            onClick={() => fetchGraph(claimId)}
            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium rounded-lg"
          >
            Explore
          </button>
        </div>
      </div>

      {/* Main Interactive Graph */}
      <InteractiveKnowledgeGraph data={graphData} loading={loading} />

      {/* Graph Analytics: Shared Devices and Ring Detection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Shared Devices Box */}
        <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
          <h3 className="text-xs font-mono uppercase text-slate-400 mb-3 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            Detected Multi-Party Shared Hardware
          </h3>
          {sharedDevices.length > 0 ? (
            <div className="space-y-2">
              {sharedDevices.map((d, i) => (
                <div key={i} className="bg-slate-950/60 border border-white/5 rounded p-2.5 text-xs font-mono flex justify-between items-center">
                  <span className="text-slate-200">{d.label}</span>
                  <span className="text-rose-400 font-bold">{d.claim_count} Claims · {d.customer_count} Customers</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 font-mono">No device multi-sharing detected in active topology.</p>
          )}
        </div>

        {/* Suspicious Ring Clusters */}
        <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
          <h3 className="text-xs font-mono uppercase text-slate-400 mb-3 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-amber-400" />
            Connected Entity Clusters & Rings
          </h3>
          {clusters.length > 0 ? (
            <div className="space-y-2">
              {clusters.map((c, i) => (
                <div key={i} className="bg-slate-950/60 border border-white/5 rounded p-2.5 text-xs font-mono flex justify-between items-center">
                  <span className="text-slate-200">{c.cluster_id}</span>
                  <span className="text-amber-400 font-bold">{c.node_count} Connected Entities</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 font-mono">No suspicious rings detected.</p>
          )}
        </div>
      </div>
    </div>
  );
};
