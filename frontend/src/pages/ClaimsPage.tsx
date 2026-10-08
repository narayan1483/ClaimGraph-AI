/**
 * ClaimGraph AI — Enterprise Claims Management Console.
 * Real backend-connected table with dynamic filtering, search, pagination, and status tracking.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { claimsService, type ClaimItem } from '@/services/claims';
import { CreateClaimModal } from './CreateClaimModal';

const STATUS_TABS = [
  { id: 'ALL', label: 'All Ingested' },
  { id: 'SUBMITTED', label: 'Submitted' },
  { id: 'UNDER_REVIEW', label: 'Under Review' },
  { id: 'FLAGGED_INVESTIGATION', label: 'Flagged / Suspicious' },
  { id: 'APPROVED', label: 'Approved' },
  { id: 'REJECTED', label: 'Rejected' },
];

export const ClaimsPage: React.FC = () => {
  const navigate = useNavigate();
  const [claims, setClaims] = useState<ClaimItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination State
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [claimType, setClaimType] = useState('ALL');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);

  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchClaims = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const query: any = {
        page,
        page_size: pageSize,
      };
      if (selectedStatus !== 'ALL') query.status = selectedStatus;
      if (claimType !== 'ALL') query.claim_type = claimType;
      if (search.trim()) query.search = search.trim();

      const response = await claimsService.listClaims(query);
      setClaims(response.data || []);
      setTotal(response.total);
    } catch (err: any) {
      console.error('Error fetching claims', err);
      setError(err?.response?.data?.message || err?.message || 'Failed to fetch claims.');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, selectedStatus, claimType, search]);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const handleClaimCreated = (newClaim: ClaimItem) => {
    fetchClaims();
    navigate(`/claims/${newClaim.claim_id || newClaim.id}`);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUBMITTED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-blue-950/60 text-blue-400 border border-blue-800/60">
            SUBMITTED
          </span>
        );
      case 'UNDER_REVIEW':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-amber-950/60 text-amber-400 border border-amber-800/60">
            UNDER REVIEW
          </span>
        );
      case 'FLAGGED_INVESTIGATION':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-rose-950/80 text-rose-300 border border-rose-800/80 animate-pulse">
            FLAGGED INVESTIGATION
          </span>
        );
      case 'APPROVED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
            APPROVED
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-slate-800 text-slate-400 border border-slate-700">
            REJECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-slate-900 text-slate-400 border border-slate-800">
            {status}
          </span>
        );
    }
  };

  const getRiskBadge = (prob?: number | null, _level?: string | null) => {
    if (prob === undefined || prob === null) {
      return <span className="text-[11px] text-slate-500 font-mono">PENDING_EVAL</span>;
    }
    const percent = (prob * 100).toFixed(1);
    if (prob >= 0.75) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-rose-950/90 text-rose-300 border border-rose-700/80">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span>
          CRITICAL ({percent}%)
        </span>
      );
    }
    if (prob >= 0.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-amber-950/70 text-amber-400 border border-amber-800/60">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          HIGH ({percent}%)
        </span>
      );
    }
    if (prob >= 0.25) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-yellow-950/50 text-yellow-400 border border-yellow-800/50">
          MEDIUM ({percent}%)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-950/50 text-emerald-400 border border-emerald-800/50">
        LOW ({percent}%)
      </span>
    );
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#162032]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></span>
            <h1 className="text-xl font-bold tracking-tight text-slate-100 font-sans">
              Claims Operations & Triage
            </h1>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Real-time policyholder claims queue with integrated ML fraud risk scoring
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchClaims()}
            className="px-3 py-1.5 text-xs font-mono text-slate-300 hover:text-white bg-[#0f172a] hover:bg-[#1e293b] border border-[#1e293b] rounded-lg transition-colors flex items-center gap-1.5"
            title="Refresh claims telemetry"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-1.5 text-xs font-medium font-mono text-slate-950 bg-gradient-to-r from-cyan-400 to-teal-400 hover:from-cyan-300 hover:to-teal-300 rounded-lg shadow-lg shadow-cyan-950/40 transition-all uppercase tracking-wider flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>File New Claim</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs & Search Ribbon */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-[#0a0f1d] border border-[#162032] p-3 rounded-xl">
        {/* Status Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 lg:pb-0 scrollbar-none">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setSelectedStatus(tab.id);
                setPage(1);
              }}
              className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all whitespace-nowrap ${
                selectedStatus === tab.id
                  ? 'bg-cyan-950/70 text-cyan-300 border border-cyan-800/80 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#111827]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search & Type dropdown */}
        <div className="flex items-center gap-2.5">
          <select
            value={claimType}
            onChange={(e) => {
              setClaimType(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-1.5 bg-[#070b14] border border-[#1e293b] rounded-lg text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Loss Types</option>
            <option value="DAMAGE">DAMAGE</option>
            <option value="THEFT">THEFT</option>
            <option value="MALFUNCTION">MALFUNCTION</option>
            <option value="LOSS">LOSS</option>
            <option value="WARRANTY_REPAIR">WARRANTY_REPAIR</option>
          </select>

          <div className="relative">
            <svg
              className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search ID, location, shop..."
              className="pl-8 pr-3 py-1.5 w-52 sm:w-64 bg-[#070b14] border border-[#1e293b] rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500 placeholder-slate-600 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Claims Data Table */}
      <div className="bg-[#090d16] border border-[#162032] rounded-xl overflow-hidden shadow-xl">
        {error && (
          <div className="p-4 bg-rose-950/40 border-b border-rose-900 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0e1422] border-b border-[#162032] text-slate-400 font-mono uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-4 py-3">Claim Identifier</th>
                <th className="px-4 py-3">Loss Type</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">ML Fraud Risk</th>
                <th className="px-4 py-3">Location / Metro</th>
                <th className="px-4 py-3">Incident Date</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#131c2e]">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-500 font-mono">
                    <div className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-4 w-4 text-cyan-400" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                      </svg>
                      <span>Querying claims ledger...</span>
                    </div>
                  </td>
                </tr>
              ) : claims.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-500 font-mono">
                    No claims found matching current filter parameters.
                  </td>
                </tr>
              ) : (
                claims.map((claim) => (
                  <tr
                    key={claim.id}
                    onClick={() => navigate(`/claims/${claim.claim_id || claim.id}`)}
                    className="hover:bg-[#0f172a]/60 cursor-pointer transition-colors group"
                  >
                    <td className="px-4 py-3 font-mono font-medium text-cyan-400 group-hover:text-cyan-300">
                      {claim.claim_id}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {claim.claim_type}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-100 font-medium">
                      ${claim.claim_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(claim.status)}
                    </td>
                    <td className="px-4 py-3">
                      {getRiskBadge(claim.fraud_probability, claim.risk_level)}
                    </td>
                    <td className="px-4 py-3 text-slate-400 max-w-[160px] truncate" title={claim.location}>
                      {claim.location}
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono text-[11px]">
                      {new Date(claim.incident_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-slate-500 group-hover:text-cyan-400 transition-colors font-mono text-[11px]">
                        Inspect →
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-[#162032] bg-[#0c121f] text-xs font-mono text-slate-400">
          <div>
            Showing <span className="text-slate-200">{claims.length}</span> of{' '}
            <span className="text-slate-200">{total}</span> recorded claims
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2.5 py-1 rounded bg-[#070b14] border border-[#1e293b] disabled:opacity-40 hover:bg-[#111827] text-slate-300 transition-colors"
            >
              Previous
            </button>
            <span className="text-slate-400">
              Page {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-2.5 py-1 rounded bg-[#070b14] border border-[#1e293b] disabled:opacity-40 hover:bg-[#111827] text-slate-300 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* File Claim Modal */}
      <CreateClaimModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreated={handleClaimCreated}
      />
    </div>
  );
};
