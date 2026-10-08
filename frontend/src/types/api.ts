/**
 * ClaimGraph AI — API response types.
 *
 * Mirrors the backend's common response schemas for type-safe API calls.
 */

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  message: string;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorDetail;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export interface PaginatedResponse<T> {
  success: true;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface ReadinessStatus {
  status: string;
  checks: Record<string, boolean>;
  timestamp: string;
}
