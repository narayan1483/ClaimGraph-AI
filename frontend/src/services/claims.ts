/**
 * ClaimGraph AI — Claims API Client Service.
 */

import apiClient from './api';
import type { ApiSuccessResponse, PaginatedResponse } from '@/types';

export interface ProductBrief {
  id: string;
  name: string;
  category: string;
  manufacturer: string;
  model_number: string;
  msrp: number;
}

export interface DeviceBrief {
  id: string;
  serial_number: string;
  product_id: string;
  customer_id?: string | null;
  product?: ProductBrief | null;
  purchase_date?: string | null;
  purchase_price?: number | null;
  status: string;
}

export interface CustomerBrief {
  id: string;
  user_id: string;
  phone_number?: string | null;
  city?: string | null;
  country: string;
  risk_score: number;
  is_flagged: boolean;
  user?: {
    id: string;
    email: string;
    full_name: string;
    role: string;
  } | null;
}

export interface ClaimEventItem {
  id: string;
  claim_id: string;
  from_status?: string | null;
  to_status: string;
  actor_id?: string | null;
  reason?: string | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
}

export interface ClaimItem {
  id: string;
  claim_id: string;
  customer_id: string;
  device_id: string;
  claim_type: 'DAMAGE' | 'THEFT' | 'MALFUNCTION' | 'LOSS' | 'WARRANTY_REPAIR';
  claim_amount: number;
  incident_date: string;
  description: string;
  location: string;
  repair_shop?: string | null;
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'FLAGGED_INVESTIGATION' | 'APPROVED' | 'REJECTED' | 'ESCALATED';
  fraud_probability?: number | null;
  risk_level?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClaimDetailItem extends ClaimItem {
  customer?: CustomerBrief | null;
  device?: DeviceBrief | null;
  events: ClaimEventItem[];
}

export interface ClaimCreateParams {
  customer_id: string;
  device_id: string;
  claim_type: string;
  claim_amount: number;
  incident_date: string;
  description: string;
  location: string;
  repair_shop?: string;
}

export interface ClaimFilterQuery {
  status?: string;
  claim_type?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export const claimsService = {
  async listClaims(params?: ClaimFilterQuery): Promise<PaginatedResponse<ClaimItem>> {
    const response = await apiClient.get<PaginatedResponse<ClaimItem>>('/claims', { params });
    return response.data;
  },

  async getClaim(identifier: string): Promise<ClaimDetailItem> {
    const response = await apiClient.get<ApiSuccessResponse<ClaimDetailItem>>(`/claims/${identifier}`);
    return response.data.data;
  },

  async createClaim(data: ClaimCreateParams): Promise<ClaimItem> {
    const response = await apiClient.post<ApiSuccessResponse<ClaimItem>>('/claims', data);
    return response.data.data;
  },

  async transitionStatus(identifier: string, status: string, reason?: string): Promise<ClaimDetailItem> {
    const response = await apiClient.patch<ApiSuccessResponse<ClaimDetailItem>>(
      `/claims/${identifier}/status`,
      { status, reason },
    );
    return response.data.data;
  },

  async evaluateFraud(identifier: string): Promise<any> {
    const response = await apiClient.post<ApiSuccessResponse<any>>(
      `/fraud/claims/${identifier}/evaluate`,
    );
    return response.data.data;
  },
};
