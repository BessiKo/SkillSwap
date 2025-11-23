import { apiClient } from './api';
import { 
  PhoneRequest, 
  CodeVerifyRequest, 
  TokenResponse, 
  CodeRequestResponse
} from '../types/auth';

export const authService = {
  async requestCode(phone: string): Promise<CodeRequestResponse> {
    const data: PhoneRequest = { phone };
    return apiClient.post<CodeRequestResponse>('/auth/request_code', data);
  },

  async verifyCode(phone: string, code: string): Promise<TokenResponse> {
    const data: CodeVerifyRequest = { phone, code };
    const response = await apiClient.post<TokenResponse>('/auth/verify_code', data);
    
    if (response.access_token) {
      apiClient.setAccessToken(response.access_token);
      localStorage.setItem('access_token', response.access_token);
    }
    
    return response;
  },

  async refreshToken(): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/refresh_token');
    
    if (response.access_token) {
      apiClient.setAccessToken(response.access_token);
      localStorage.setItem('access_token', response.access_token);
    }
    
    return response;
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
    apiClient.setAccessToken(null);
    localStorage.removeItem('access_token');
  },

  restoreSession(): void {
    const token = localStorage.getItem('access_token');
    if (token) {
      apiClient.setAccessToken(token);
    }
  },

  isTokenValid(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }
};