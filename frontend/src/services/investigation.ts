/**
 * ClaimGraph AI — Investigation, Knowledge Graph & RAG Service API Client.
 */

import api from './api';

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
  risk_level?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphDataResponse {
  nodes: GraphNode[];
  links: GraphLink[];
  node_count: number;
  link_count: number;
  claim_id?: string;
}

export interface GraphRiskResult {
  claim_id: string;
  graph_risk_score: number;
  degree: number;
  centrality: number;
  connected_cluster_size: number;
  shared_device_detected: boolean;
  shared_location_detected: boolean;
  suspicious_repair_shop_detected: boolean;
  repeat_claim_velocity_detected: boolean;
  evidence: string[];
  signals: Array<{
    name: string;
    severity: string;
    evidence: string;
    score_impact: number;
  }>;
}

export interface RAGChunk {
  chunk_id: string;
  document: string;
  section: string;
  content: string;
  similarity_score: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  sources: string[];
  retrieved_chunks: RAGChunk[];
  model: string;
  latency_ms: number;
  token_usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  grounded: boolean;
}

export interface AgentResultItem {
  agent_name: string;
  status: string;
  result: Record<string, any>;
  evidence: string[];
  confidence: number;
  source: string;
  latency_ms: number;
}

export interface InvestigationRunResponse {
  investigation_id: string;
  claim_id: string;
  fraud_score: number;
  graph_score: number;
  final_risk_score: number;
  risk_level: string;
  recommendation: string;
  evidence: Array<{
    category: string;
    text: string;
    source?: string;
    weight?: number;
  }>;
  agent_results: Record<string, AgentResultItem>;
  investigation_report: string;
  score_breakdown: Record<string, number>;
  status: string;
}

export interface AdjudicationResponse {
  investigation_id: string;
  claim_id: string;
  decision: string;
  new_claim_status: string;
  message: string;
  decided_at: string;
}

export const investigationService = {
  /**
   * Run full LangGraph AI multi-agent investigation.
   */
  async runInvestigation(claimId: string): Promise<InvestigationRunResponse> {
    const res = await api.post<InvestigationRunResponse>(`/investigations/${claimId}/run`);
    return res.data;
  },

  /**
   * Fetch existing investigation record for a claim.
   */
  async getInvestigation(claimId: string): Promise<InvestigationRunResponse> {
    const res = await api.get<InvestigationRunResponse>(`/investigations/${claimId}`);
    return res.data;
  },

  /**
   * Record human investigator adjudication decision.
   */
  async recordDecision(
    investigationId: string,
    decision: 'APPROVE' | 'REJECT' | 'ESCALATE' | 'REQUEST_MORE_INFO',
    notes?: string,
    badgeNumber?: string
  ): Promise<AdjudicationResponse> {
    const res = await api.post<AdjudicationResponse>(`/investigations/${investigationId}/decision`, {
      decision,
      notes,
      badge_number: badgeNumber,
    });
    return res.data;
  },

  /**
   * Fetch real Neo4j knowledge graph subgraph for claim.
   */
  async getClaimGraph(claimId: string, hops: number = 2): Promise<GraphDataResponse> {
    const res = await api.get<GraphDataResponse>(`/graph/claim/${claimId}`, {
      params: { hops },
    });
    return res.data;
  },

  /**
   * Fetch graph-based fraud signals and risk score.
   */
  async getGraphRisk(claimId: string): Promise<GraphRiskResult> {
    const res = await api.get<GraphRiskResult>(`/graph/risk/${claimId}`);
    return res.data;
  },

  /**
   * Query RAG policy knowledge engine.
   */
  async queryPolicy(query: string, claimId?: string, policyType?: string): Promise<RAGQueryResponse> {
    const res = await api.post<RAGQueryResponse>('/rag/query', {
      query,
      claim_id: claimId,
      policy_type: policyType,
    });
    return res.data;
  },

  /**
   * List indexed policy documents and statistics.
   */
  async listPolicies(): Promise<{ indexed_documents: string[]; total_chunks: number; status: string }> {
    const res = await api.get('/rag/policies');
    return res.data;
  },

  /**
   * Fetch suspicious network clusters from graph analytics.
   */
  async getGraphClusters(): Promise<{ clusters: any[]; shared_devices: any[]; suspicious_repair_shops: any[] }> {
    const res = await api.get('/graph/analytics/clusters');
    return res.data;
  },
};
