/**
 * ClaimGraph AI — Enterprise Dashboard Layout.
 *
 * Professional high-density workspace shell inspired by Palantir Foundry & Linear.
 * Clean lines, surgical typography, and zero generic AI bloat.
 */

import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  ShieldAlert,
  Network,
  FolderOpen,
  BarChart2,
  TrendingUp,
  Cpu,
  Layers,
  ScrollText,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bell,
  Search,
  LogOut,
  Shield,
  Activity,
  Terminal,
  Sun,
  Moon,
  Palette,
} from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  section: string;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  // ── Operations ──
  { label: 'Overview',            path: '/',                    icon: <LayoutDashboard size={16} />, section: 'WORKSPACE' },
  { label: 'Claims Queue',        path: '/claims',              icon: <FileText size={16} />,        section: 'WORKSPACE', badge: 'Active' },
  { label: 'Documents & Evidence',path: '/documents',           icon: <FolderOpen size={16} />,      section: 'WORKSPACE' },

  // ── Intelligence Core ──
  { label: 'Investigation Desk',  path: '/investigation',       icon: <ShieldAlert size={16} />,     section: 'INTELLIGENCE', badge: 'Core' },
  { label: 'Fraud Detection ML',  path: '/fraud',               icon: <Layers size={16} />,          section: 'INTELLIGENCE' },
  { label: 'Knowledge Graph 3D',  path: '/graph',               icon: <Network size={16} />,         section: 'INTELLIGENCE' },
  { label: 'Policy Intelligence', path: '/policy',              icon: <FileText size={16} />,        section: 'INTELLIGENCE' },

  // ── Telemetry & Evaluation ──
  { label: 'Loss Analytics',      path: '/analytics',           icon: <BarChart2 size={16} />,       section: 'TELEMETRY' },
  { label: 'Model Registry',      path: '/model-performance',   icon: <TrendingUp size={16} />,      section: 'TELEMETRY' },
  { label: 'LLM Fidelity Eval',   path: '/ai-evaluation',       icon: <Cpu size={16} />,             section: 'TELEMETRY' },
  { label: 'Drift & Data Monitor',path: '/drift',               icon: <Activity size={16} />,        section: 'TELEMETRY' },

  // ── Governance ──
  { label: 'Audit Trail',         path: '/audit',               icon: <ScrollText size={16} />,      section: 'GOVERNANCE' },
  { label: 'Access Control',      path: '/users',               icon: <Users size={16} />,           section: 'GOVERNANCE' },
  { label: 'System Settings',     path: '/settings',            icon: <Settings size={16} />,        section: 'GOVERNANCE' },
];

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const sections = [...new Set(NAV_ITEMS.map((item) => item.section))];
  const activeItem = NAV_ITEMS.find((item) => item.path === location.pathname);

  return (
    <div className="flex h-screen overflow-hidden bg-[#07090e] text-[#f1f5f9]">
      {/* ── Sidebar ── */}
      <aside
        className={clsx(
          'flex flex-col border-r border-[#192233] bg-[#0b0e14] transition-all duration-200 select-none',
          collapsed ? 'w-[58px]' : 'w-[240px]',
        )}
      >
        {/* Brand Header */}
        <div className="flex h-14 items-center justify-between border-b border-[#192233] px-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded bg-[#1e293b] border border-[#334155] text-white font-mono text-xs font-semibold">
              <Shield size={14} className="text-blue-400" />
            </div>
            {!collapsed && (
              <div className="truncate">
                <span className="text-xs font-bold tracking-wider uppercase text-slate-100">ClaimGraph</span>
                <span className="text-[10px] text-blue-400 font-mono ml-1.5 font-semibold">AI</span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex h-6 w-6 items-center justify-center text-slate-500 hover:text-slate-200 hover:bg-[#151c28] rounded transition-colors"
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
          {sections.map((section) => (
            <div key={section}>
              {!collapsed && (
                <p className="px-2.5 pb-1.5 text-[9px] font-mono font-semibold tracking-wider text-slate-500 uppercase">
                  {section}
                </p>
              )}
              <ul className="space-y-0.5">
                {NAV_ITEMS.filter((item) => item.section === section).map((item) => (
                  <li key={item.path}>
                    <NavLink
                      to={item.path}
                      className={({ isActive }) =>
                        clsx(
                          'flex items-center gap-2.5 rounded px-2.5 py-1.5 text-xs font-medium transition-colors',
                          isActive
                            ? 'bg-[#152033] text-blue-400 border-l-2 border-blue-500'
                            : 'text-slate-400 hover:bg-[#101622] hover:text-slate-200',
                          collapsed && 'justify-center px-1.5',
                        )
                      }
                      end={item.path === '/'}
                    >
                      <span className="shrink-0">{item.icon}</span>
                      {!collapsed && (
                        <div className="flex flex-1 items-center justify-between truncate">
                          <span className="truncate">{item.label}</span>
                          {item.badge && (
                            <span className="ml-1.5 rounded bg-[#1e293b] px-1.5 py-0.2 text-[9px] font-mono text-slate-400">
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* User Identity Footer in Sidebar */}
        <div className="border-t border-[#192233] p-2">
          {!collapsed ? (
            <div className="flex items-center justify-between rounded bg-[#0e121a] p-2 border border-[#192233]">
              <div className="min-w-0 pr-2">
                <p className="truncate text-xs font-semibold text-slate-200">
                  {user?.full_name || 'Narayan Prasad Maurya'}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span className="text-[10px] font-mono uppercase text-slate-400">
                    {user?.role || 'INVESTIGATOR'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => logout()}
                title="Log out"
                className="text-slate-400 hover:text-rose-400 p-1 rounded hover:bg-[#1a2333] transition-colors"
              >
                <LogOut size={14} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => logout()}
              title="Log out"
              className="flex w-full justify-center p-2 text-slate-400 hover:text-rose-400 rounded hover:bg-[#1a2333] transition-colors"
            >
              <LogOut size={16} />
            </button>
          )}
        </div>
      </aside>

      {/* ── Workspace Area ── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Control Bar */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-[#192233] bg-[#090d14] px-5">
          {/* Breadcrumbs */}
          <div className="flex items-center gap-2 text-xs">
            <span className="font-mono text-slate-500 uppercase text-[10px]">CLAIMGRAPH</span>
            <span className="text-slate-600">/</span>
            <span className="font-semibold text-slate-200">{activeItem?.label || 'Overview'}</span>
          </div>

          {/* Quick Search & Platform Status */}
          <div className="flex items-center gap-3">
            <div className="relative hidden md:flex items-center">
              <Search size={13} className="absolute left-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search claims, policy IDs, VIN..."
                className="h-8 w-64 rounded bg-[#0e121a] border border-[#192233] pl-8 pr-12 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
              <kbd className="absolute right-2 rounded border border-[#243048] bg-[#141a26] px-1.5 py-0.5 text-[9px] font-mono text-slate-400">
                ⌘K
              </kbd>
            </div>

            <div className="h-4 w-px bg-[#192233]" />

            {/* Live System Indicator */}
            <div className="flex items-center gap-1.5 rounded border border-emerald-900/40 bg-emerald-950/20 px-2 py-1 text-[11px] font-mono text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>CLUSTER LIVE</span>
            </div>

            {/* Theme Selector: Dark (Obsidian) | White (Light) | Navy (Cyber) */}
            <div className="flex items-center rounded-lg border border-[#192233] bg-[#0c1018] p-0.5 text-xs font-mono">
              <button
                onClick={() => setTheme('dark')}
                className={clsx(
                  'flex items-center gap-1 px-2 py-1 rounded text-[11px] transition-all',
                  theme === 'dark'
                    ? 'bg-[#192233] text-cyan-400 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                )}
                title="Black Obsidian Stealth Theme"
              >
                <Moon size={12} />
                <span className="hidden sm:inline">Black</span>
              </button>
              <button
                onClick={() => setTheme('light')}
                className={clsx(
                  'flex items-center gap-1 px-2 py-1 rounded text-[11px] transition-all',
                  theme === 'light'
                    ? 'bg-slate-200 text-slate-900 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                )}
                title="Clean White Enterprise Theme"
              >
                <Sun size={12} />
                <span className="hidden sm:inline">White</span>
              </button>
              <button
                onClick={() => setTheme('navy')}
                className={clsx(
                  'flex items-center gap-1 px-2 py-1 rounded text-[11px] transition-all',
                  theme === 'navy'
                    ? 'bg-blue-900 text-blue-200 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                )}
                title="Cyber Navy Slate Theme"
              >
                <Palette size={12} />
                <span className="hidden sm:inline">Navy</span>
              </button>
            </div>

            {/* Sign In / Switch Account Button */}
            <NavLink
              to="/login"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-[#192233] bg-[#0e121a] hover:bg-[#152033] hover:border-cyan-500/50 text-xs font-mono text-slate-300 hover:text-cyan-300 transition-colors"
              title="Sign in or switch role account"
            >
              <Users size={12} className="text-cyan-400" />
              <span>Sign In / Switch</span>
            </NavLink>

            <button className="relative text-slate-400 hover:text-slate-200 p-1.5 rounded hover:bg-[#151c28] transition-colors">
              <Bell size={15} />
            </button>
          </div>
        </header>

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-5 bg-[#07090e]">
          <Outlet />
        </main>

        {/* Surgical Status Ribbon (Footer) */}
        <footer className="flex h-7 shrink-0 items-center justify-between border-t border-[#192233] bg-[#080b11] px-4 text-[10px] font-mono text-slate-500 select-none">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Terminal size={11} className="text-blue-400" />
              <span>CORE v0.2.0</span>
            </span>
            <span>API: 200 OK (2.4ms)</span>
            <span>EVENT_BUS: KAFKA ACTIVE</span>
          </div>
          <div className="flex items-center gap-3">
            <span>OPERATOR: {user?.full_name || 'N. P. MAURYA'}</span>
            <span className="text-slate-600">|</span>
            <span className="text-emerald-500">TAMPER_LOGGING: ON</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
