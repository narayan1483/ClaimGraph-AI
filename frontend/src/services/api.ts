/**
 * ClaimGraph AI — Axios HTTP client.
 *
 * Pre-configured axios instance with interceptors for auth tokens,
 * request/response logging, and error normalization.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor — attach JWT token ──
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor — normalise errors ──
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Future: redirect to login or trigger auth refresh
    }
    return Promise.reject(error);
  },
);

export default apiClient;
