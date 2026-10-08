/**
 * ClaimGraph AI — Auth API Service.
 *
 * Handles HTTP requests for login, registration, token refresh, and profile inspection.
 */

import apiClient from './api';
import type {
  ApiSuccessResponse,
  LoginCredentials,
  RegisterPayload,
  TokenResponse,
  UserDetail,
} from '@/types';

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<ApiSuccessResponse<TokenResponse>>(
      '/auth/login',
      credentials,
    );
    return response.data.data;
  },

  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const response = await apiClient.post<ApiSuccessResponse<TokenResponse>>(
      '/auth/register',
      payload,
    );
    return response.data.data;
  },

  async getCurrentUser(): Promise<UserDetail> {
    const response = await apiClient.get<ApiSuccessResponse<UserDetail>>('/auth/me');
    return response.data.data;
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<ApiSuccessResponse<TokenResponse>>(
      '/auth/refresh',
      { refresh_token: refreshToken },
    );
    return response.data.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Ignore network errors on logout
    }
  },
};
