/**
 * ClaimGraph AI — useHealthCheck hook.
 *
 * Polls the backend health endpoint and returns connectivity status.
 */

import { useEffect, useState, useCallback } from 'react';
import { healthService } from '@/services/health';
import type { HealthStatus } from '@/types';

interface HealthCheckState {
  status: 'loading' | 'connected' | 'disconnected';
  data: HealthStatus | null;
  error: string | null;
  refetch: () => void;
}

export function useHealthCheck(intervalMs = 30_000): HealthCheckState {
  const [status, setStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading');
  const [data, setData] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const check = useCallback(async () => {
    try {
      const result = await healthService.getHealth();
      setData(result);
      setStatus('connected');
      setError(null);
    } catch (err) {
      setStatus('disconnected');
      setError(err instanceof Error ? err.message : 'Backend unreachable');
    }
  }, []);

  useEffect(() => {
    check();
    const timer = setInterval(check, intervalMs);
    return () => clearInterval(timer);
  }, [check, intervalMs]);

  return { status, data, error, refetch: check };
}
