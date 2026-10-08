/**
 * ClaimGraph AI — Protected Route Guard.
 *
 * Restricts access to authenticated users and enforces role-based authorization.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import type { UserRole } from '@/types';
import { ShieldAlert } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-surface-950">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
          <p className="text-sm font-medium text-surface-600">Verifying session...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated && allowedRoles) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="glass max-w-md rounded-2xl p-8 text-center animate-fade-in">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-danger/15 text-danger">
            <ShieldAlert size={28} />
          </div>
          <h2 className="text-xl font-bold text-white">Access Denied</h2>
          <p className="mt-2 text-sm text-surface-600">
            Your role (<span className="font-semibold text-brand-400">{user.role}</span>) does not have
            permission to view this section.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
