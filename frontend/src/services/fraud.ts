/**
 * ClaimGraph AI — Machine Learning Fraud Intelligence API Client.
 */

import apiClient from './api';
import type { ApiSuccessResponse } from '@/types';

export interface TopFactor {
  feature: string;
  impact: number;
  direction: 'INCREASES_RISK' | 'DECREASES_RISK' | 'NEUTRAL';
  description: string;
}

export interface FraudPredictionResult {
  fraud_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  top_factors: TopFactor[];
  feature_contributions?: Record<string, number>;
  model_version: string;
  prediction_timestamp: string;
}

export interface ModelMetricsComparison {
  status: string;
  best_model: string;
  selection_criteria: string;
  timestamp: string;
  benchmark_results: Record<
    string,
    {
      precision: number;
      recall: number;
      f1_score: number;
      roc_auc: number;
      pr_auc: number;
      confusion_matrix: number[][];
    }
  >;
  best_model_metrics: {
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    confusion_matrix: number[][];
  };
}

export interface FraudPredictionRequest {
  claim_amount: number;
  previous_claim_count?: number;
  claims_last_30_days?: number;
  average_claim_amount?: number;
  amount_deviation?: number;
  amount_to_msrp_ratio?: number;
  device_claim_count?: number;
  customer_claim_frequency?: number;
  location_frequency?: number;
  repair_shop_frequency?: number;
  days_since_last_claim?: number;
  device_age?: number;
}

export const fraudService = {
  /**
   * Run direct ML inference with SHAP feature attribution
   */
  async predictFraud(features: FraudPredictionRequest): Promise<FraudPredictionResult> {
    const response = await apiClient.post<ApiSuccessResponse<FraudPredictionResult>>(
      '/fraud/predict',
      features,
    );
    return response.data.data;
  },

  /**
   * Evaluate fraud on an existing stored claim and persist the score
   */
  async evaluateClaim(claimId: string): Promise<FraudPredictionResult> {
    const response = await apiClient.post<ApiSuccessResponse<FraudPredictionResult>>(
      `/fraud/claims/${claimId}/evaluate`,
    );
    return response.data.data;
  },

  /**
   * Retrieve active model benchmarks and comparison metrics
   */
  async getModelMetrics(): Promise<ModelMetricsComparison> {
    const response = await apiClient.get<ApiSuccessResponse<ModelMetricsComparison>>('/fraud/metrics');
    return response.data.data;
  },
};
