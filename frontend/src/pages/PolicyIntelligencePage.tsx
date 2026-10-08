/**
 * ClaimGraph AI — RAG Policy Intelligence Hub Page.
 */

import React, { useState, useEffect } from 'react';
import { investigationService, type RAGQueryResponse } from '@/services/investigation';
import { Search, FileText, CheckCircle2, RotateCcw } from 'lucide-react';




export const PolicyIntelligencePage: React.FC = () => {
  const [query, setQuery] = useState('What are the grounds for warranty claim denial under accidental damage?');
  const [policies, setPolicies] = useState<string[]>([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [response, setResponse] = useState<RAGQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    investigationService.listPolicies().then((res) => {
      setPolicies(res.indexed_documents || []);
      setTotalChunks(res.total_chunks || 0);
    }).catch(console.error);
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    try {
      setLoading(true);
      const res = await investigationService.queryPolicy(query);
      setResponse(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="border-b border-white/10 pb-4">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            RAG Policy Intelligence
          </span>
          <span className="text-slate-500 text-xs font-mono">Grounded Vector Store · Anti-Hallucination Guardrails</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white mt-1">Underwriting & Fraud Guidelines Assistant</h1>
      </div>

      {/* Query Bar */}
      <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Ask question about coverage limits, proof of loss, escalation criteria..."
            className="flex-1 px-3 py-2 bg-slate-950 border border-white/10 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5"
          >
            {loading ? <RotateCcw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            <span>Search Policy</span>
          </button>
        </div>

        {/* Quick query chips */}
        <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
          <span className="text-slate-500">Quick inquiries:</span>
          {[
            'What is the mandatory deductible for ADP riders?',
            'What are the mandatory proof of loss documents?',
            'What red flags require immediate SIU referral?',
            'When does a claim exceed adjuster authority?',
          ].map((q) => (
            <button
              key={q}
              onClick={() => {
                setQuery(q);
              }}
              className="px-2 py-1 bg-white/5 hover:bg-white/10 text-slate-300 rounded border border-white/5 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Grounded Result Display */}
      {response && (
        <div className="bg-slate-900/70 border border-white/10 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-white/5 pb-2 text-xs font-mono">
            <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Grounded Response ({response.model})
            </span>
            <span className="text-slate-400">
              Latency: {response.latency_ms}ms · Tokens: {response.token_usage.total_tokens}
            </span>
          </div>

          <div className="text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
            {response.answer}
          </div>

          {/* Sources and Chunks */}
          <div className="border-t border-white/5 pt-3">
            <h4 className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2">
              Retrieved Policy Citations ({response.retrieved_chunks.length})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {response.retrieved_chunks.map((chk) => (
                <div key={chk.chunk_id} className="bg-slate-950/60 border border-white/5 rounded-lg p-3 text-xs font-mono">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <strong className="text-slate-300 truncate">{chk.document}</strong>
                    <span className="text-cyan-400">Score: {chk.similarity_score.toFixed(3)}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 block mb-1">Section: {chk.section}</span>
                  <p className="text-slate-400 text-[11px] line-clamp-4 leading-normal">{chk.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Loaded Policies Index */}
      <div className="bg-slate-900/40 border border-white/10 rounded-xl p-4">
        <h3 className="text-xs font-mono uppercase text-slate-400 mb-2">
          Indexed Regulatory & Underwriting Policies ({policies.length} Documents · {totalChunks} Chunks)
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 font-mono text-xs text-slate-300">
          {policies.map((p) => (
            <div key={p} className="p-2 rounded bg-slate-950/50 border border-white/5 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
              <span className="truncate">{p}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
