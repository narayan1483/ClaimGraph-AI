/**
 * ClaimGraph AI — Authentication & User TypeScript types.
 */

export type UserRole = 'ADMIN' | 'INVESTIGATOR' | 'ANALYST' | 'CUSTOMER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  organization_id?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface CustomerProfile {
  id: string;
  user_id: string;
  phone_number?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  country: string;
  risk_score: number;
  is_flagged: boolean;
}

export interface InvestigatorProfile {
  id: string;
  user_id: string;
  badge_number?: string | null;
  specialization?: string | null;
  cases_resolved: number;
}

export interface UserDetail extends User {
  customer_profile?: CustomerProfile | null;
  investigator_profile?: InvestigatorProfile | null;
  organization?: {
    id: string;
    name: string;
    slug: string;
  } | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role?: UserRole;
  organization_id?: string | null;
}
