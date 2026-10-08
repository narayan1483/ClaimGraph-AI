/**
 * ClaimGraph AI — Health service.
 */

import apiClient from './api';
import type { HealthStatus, ReadinessStatus } from '@/types';

export const healthService = {
  async getHealth(): Promise<HealthStatus> {
    const { data } = await apiClient.get<HealthStatus>('/health');
    return data;
  },

  async getReadiness(): Promise<ReadinessStatus> {
    const { data } = await apiClient.get<ReadinessStatus>('/health/ready');
    return data;
  },
};
