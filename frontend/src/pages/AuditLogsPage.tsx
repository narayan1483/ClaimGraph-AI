import React, { useEffect, useState } from 'react';
import apiClient from '@/services/api';
import { ShieldCheck, RefreshCw, Filter, Search, Clock, UserCheck, AlertTriangle } from 'lucide-react';

interface AuditItem {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: Record<string, any> | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
}

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionFilter, setActionFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = { limit: 50 };
      if (actionFilter) params.action = actionFilter;
      const res = await apiClient.get('/audit/logs', { params });
      if (res.data?.data) {
        setLogs(res.data.data);
      } else if (Array.isArray(res.data)) {
        setLogs(res.data);
      }
    } catch (err: any) {
      console.error('Failed to load audit logs:', err);
      setError(err?.response?.data?.detail || 'Unable to retrieve audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const filteredLogs = logs.filter((log) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      log.action.toLowerCase().includes(q) ||
      (log.entity_id && log.entity_id.toLowerCase().includes(q)) ||
      (log.user_id && log.user_id.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            Security & Compliance Audit Trail
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable, tamper-evident chronological event log of all system transitions and human investigator decisions.
          </p>
        </div>
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search by action, user ID, or entity ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 px-3 py-2 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Actions</option>
            <option value="CLAIM_CREATED">Claim Created</option>
            <option value="INVESTIGATION_COMPLETED">Investigation Completed</option>
            <option value="CLAIM_DECIDED_APPROVE">Approved Claims</option>
            <option value="CLAIM_DECIDED_REJECT">Rejected Claims</option>
            <option value="CLAIM_DECIDED_ESCALATE">Escalated Claims</option>
          </select>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/80 text-xs font-semibold uppercase text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Entity</th>
                <th className="px-6 py-4">Actor</th>
                <th className="px-6 py-4">Event Details & State</th>
                <th className="px-6 py-4">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {loading && logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500 font-sans">
                    Loading audit trail events...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500 font-sans">
                    No matching audit log records found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => {
                  const isDecision = log.action.includes('DECIDED');
                  const isApprove = log.action.includes('APPROVE');
                  const isReject = log.action.includes('REJECT');

                  let badgeColor = 'bg-blue-950/80 text-blue-400 border-blue-800';
                  if (isApprove) badgeColor = 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
                  else if (isReject) badgeColor = 'bg-red-950/80 text-red-400 border-red-800';
                  else if (isDecision) badgeColor = 'bg-amber-950/80 text-amber-400 border-amber-800';

                  return (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition">
                      <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 font-sans">
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                          {new Date(log.created_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-block px-2.5 py-1 rounded text-[11px] font-semibold border ${badgeColor}`}>
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-sans">
                        <span className="text-slate-400">{log.entity_type}:</span>{' '}
                        <span className="font-mono text-slate-200">{log.entity_id ? log.entity_id.slice(0, 12) + '...' : 'N/A'}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-400 font-sans">
                        <div className="flex items-center gap-1.5">
                          <UserCheck className="w-3.5 h-3.5 text-slate-500" />
                          {log.user_id ? log.user_id.slice(0, 8) + '...' : 'SYSTEM_WORKER'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="max-w-md max-h-24 overflow-y-auto bg-slate-950 p-2 rounded border border-slate-800/80 text-[11px] text-slate-400">
                          {log.details ? JSON.stringify(log.details, null, 2) : 'No details recorded'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-500 whitespace-nowrap">
                        {log.ip_address || '127.0.0.1'}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
