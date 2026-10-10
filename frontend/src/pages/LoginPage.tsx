/**
 * ClaimGraph AI — Enterprise Login & Registration Page.
 *
 * Production authentication view with credential verification and persona presets.
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  Lock,
  Mail,
  User as UserIcon,
  AlertCircle,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export default function LoginPage() {
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const rawFrom = (location.state as { from?: { pathname: string } })?.from?.pathname;
  const targetPath = (!rawFrom || rawFrom === '/login' || rawFrom.startsWith('/login')) ? '/' : rawFrom;

  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('investigator@claimgraph.ai');
  const [password, setPassword] = useState('InvestigatorPass123!');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'INVESTIGATOR' | 'ADMIN' | 'ANALYST' | 'CUSTOMER'>('INVESTIGATOR');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // If already logged in with stored JWT token, redirect to target
  React.useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && isAuthenticated) {
      navigate(targetPath, { replace: true });
    }
  }, [isAuthenticated, navigate, targetPath]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setLoading(true);

    try {
      if (isRegister) {
        await register({
          email: email.trim(),
          password: password.trim(),
          full_name: fullName.trim(),
          role,
        });
      } else {
        await login({ email: email.trim(), password: password.trim() });
      }
      navigate(targetPath, { replace: true });
    } catch (err: unknown) {
      console.error('Login submit error:', err);
      setErrorMessage(
        err instanceof Error ? err.message : 'Authentication failed. Please verify credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Demo presets for easy investigator testing
  const handlePreset = (presetRole: 'INVESTIGATOR' | 'ADMIN' | 'CUSTOMER') => {
    setIsRegister(false);
    if (presetRole === 'INVESTIGATOR') {
      setEmail('investigator@claimgraph.ai');
      setPassword('InvestigatorPass123!');
    } else if (presetRole === 'ADMIN') {
      setEmail('admin@claimgraph.ai');
      setPassword('AdminPass123!');
    } else {
      setEmail('customer@example.com');
      setPassword('CustomerPass123!');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-950 p-4">
      {/* Background glow effects */}
      <div className="pointer-events-none fixed inset-0 flex items-center justify-center">
        <div className="h-[450px] w-[450px] rounded-full bg-brand-600/10 blur-[120px]" />
      </div>

      <div className="glass relative z-10 w-full max-w-md rounded-2xl p-8 shadow-2xl animate-fade-in border border-surface-700/60">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-white font-bold text-lg shadow-lg shadow-brand-600/30">
            CG
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">ClaimGraph AI</h1>
          <p className="mt-1 text-xs uppercase tracking-widest text-surface-600 font-semibold">
            Fraud & Claims Intelligence
          </p>
        </div>

        {/* Direct Platform Access (No Mandatory Login) */}
        <div className="mt-4 mb-2 flex items-center justify-between rounded-lg border border-cyan-800/60 bg-cyan-950/40 px-3 py-2 text-xs font-mono">
          <span className="text-slate-300">Explore workspace directly:</span>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="font-bold text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 uppercase tracking-wider"
          >
            <span>Enter Platform →</span>
          </button>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mt-5 flex items-center gap-2.5 rounded-lg border border-danger/30 bg-danger/10 p-3 text-xs text-danger animate-fade-in">
            <AlertCircle size={16} className="shrink-0" />
            <p>{errorMessage}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <UserIcon
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-600"
                />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full rounded-lg border border-surface-700/60 bg-surface-900/80 py-2.5 pl-10 pr-4 text-sm text-white placeholder-surface-600 focus:border-brand-500 focus:outline-none transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-surface-600 mb-1.5">
              Work Email
            </label>
            <div className="relative">
              <Mail
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-600"
              />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@claimgraph.ai"
                className="w-full rounded-lg border border-surface-700/60 bg-surface-900/80 py-2.5 pl-10 pr-4 text-sm text-white placeholder-surface-600 focus:border-brand-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-surface-600 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-600"
              />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-surface-700/60 bg-surface-900/80 py-2.5 pl-10 pr-4 text-sm text-white placeholder-surface-600 focus:border-brand-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1.5">
                Role Persona
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as typeof role)}
                className="w-full rounded-lg border border-surface-700/60 bg-surface-900/80 py-2.5 px-3 text-sm text-white focus:border-brand-500 focus:outline-none transition-colors"
              >
                <option value="INVESTIGATOR">Investigator (Claims & Fraud Review)</option>
                <option value="ANALYST">Analyst (Monitoring & Metrics)</option>
                <option value="ADMIN">Admin (Full System Control)</option>
                <option value="CUSTOMER">Customer (Claimant)</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-500 disabled:opacity-50"
          >
            {loading ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <>
                <span>{isRegister ? 'Create Account' : 'Sign In to Workspace'}</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        {/* Toggle between Login and Register */}
        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setErrorMessage(null);
            }}
            className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors"
          >
            {isRegister
              ? 'Already registered? Sign in instead'
              : 'New investigator or claimant? Register account'}
          </button>
        </div>

        {/* Quick Persona Presets for fast testing */}
        {!isRegister && (
          <div className="mt-6 border-t border-surface-700/40 pt-4">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-2">
              <Sparkles size={12} className="text-brand-400" />
              <span>Quick Test Fill</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handlePreset('INVESTIGATOR')}
                className="rounded border border-surface-700/50 bg-surface-800/40 py-1.5 text-[11px] font-medium text-surface-600 hover:text-white hover:bg-surface-800 transition-colors"
              >
                Investigator
              </button>
              <button
                type="button"
                onClick={() => handlePreset('ADMIN')}
                className="rounded border border-surface-700/50 bg-surface-800/40 py-1.5 text-[11px] font-medium text-surface-600 hover:text-white hover:bg-surface-800 transition-colors"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => handlePreset('CUSTOMER')}
                className="rounded border border-surface-700/50 bg-surface-800/40 py-1.5 text-[11px] font-medium text-surface-600 hover:text-white hover:bg-surface-800 transition-colors"
              >
                Customer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
