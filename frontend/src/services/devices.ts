/**
 * ClaimGraph AI — Devices & Products API Client Service.
 */

import apiClient from './api';
import type { ApiSuccessResponse } from '@/types';
import type { DeviceBrief, ProductBrief } from './claims';

export const devicesService = {
  /**
   * List customer devices available in the system
   */
  async listDevices(): Promise<DeviceBrief[]> {
    const response = await apiClient.get<ApiSuccessResponse<DeviceBrief[]>>('/devices');
    return response.data.data;
  },

  /**
   * List product catalog items
   */
  async listProducts(): Promise<ProductBrief[]> {
    const response = await apiClient.get<ApiSuccessResponse<ProductBrief[]>>('/devices/products');
    return response.data.data;
  },
};
