import { UserRole } from './index';

export interface PhoneRequest {
  phone: string;
}

export interface CodeVerifyRequest {
  phone: string;
  code: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  is_new_user: boolean;
}

export interface CodeRequestResponse {
  message: string;
  expires_in: number;
  debug_code?: string;
}

export interface TokenPayload {
  sub: string;
  role: UserRole;
  exp: number;
  type: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  tokens: {
    accessToken: string | null;
  };
  loading: boolean;
}