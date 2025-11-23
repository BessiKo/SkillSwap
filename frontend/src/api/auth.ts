import { apiClient } from './client';
import type { TokenResponse, CodeRequestResponse } from '../types';

export const authApi = {
  requestCode: (phone: string): Promise<CodeRequestResponse> => {
    return apiClient.post('/auth/request_code', { phone }, { skipAuth: true });
  },

  verifyCode: async (phone: string, code: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      '/auth/verify_code',
      { phone, code },
      { skipAuth: true }
    );
    apiClient.setToken(response.access_token);
    return response;
  },

  refreshToken: (): Promise<TokenResponse> => {
    return apiClient.post('/auth/refresh', null, { skipAuth: true });
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout', null, { skipAuth: true });
    apiClient.setToken(null);
  },
};