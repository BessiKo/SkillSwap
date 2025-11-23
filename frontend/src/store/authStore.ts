import { create } from 'zustand';
import type { User } from '../types';
import { authApi } from '../api/auth';
import { usersApi } from '../api/users';
import { apiClient } from '../api/client';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isNewUser: boolean;
  
  requestCode: (phone: string) => Promise<{ success: boolean; debugCode?: string; error?: string }>;
  verifyCode: (phone: string, code: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
  clearNewUserFlag: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  isNewUser: false,

  requestCode: async (phone) => {
    try {
      const res = await authApi.requestCode(phone);
      return { success: true, debugCode: res.debug_code };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  },

  verifyCode: async (phone, code) => {
    try {
      const res = await authApi.verifyCode(phone, code);
      set({ isNewUser: res.is_new_user, isAuthenticated: true });
      await get().fetchUser();
      return { success: true };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } finally {
      apiClient.setToken(null); 
      set({ user: null, isAuthenticated: false, isLoading: false, isNewUser: false });
    }
  },

  fetchUser: async () => {
    try {
      const user = await usersApi.getMe();
      set({ user, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
    }
  },

  checkAuth: async () => {
    set({ isLoading: true });
    const token = apiClient.getToken();
    
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return false;
    }
    
    try {
      await get().fetchUser();
      set({ isLoading: false, isAuthenticated: true });
      return true;
    } catch (e) {
      const newToken = await apiClient.refreshToken(); 

      if (newToken) {
        try {
          await get().fetchUser();
          set({ isLoading: false, isAuthenticated: true });
          return true;
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false });
          return false;
        }
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return false;
      }
    }
  },

  clearNewUserFlag: () => {
    set({ isNewUser: false });
  }
}));