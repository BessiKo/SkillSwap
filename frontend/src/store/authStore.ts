import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthState } from '../types/auth';
import { UserProfileOut } from '../types/user';

interface AuthStore extends AuthState {
  setUser: (user: UserProfileOut) => void;
  setTokens: (tokens: { accessToken: string }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      tokens: { accessToken: null },
      loading: false,
      
      setUser: (user) => set({ user }),
      setTokens: (tokens) => set({ tokens }),
      clearAuth: () => set({ 
        isAuthenticated: false, 
        user: null, 
        tokens: { accessToken: null } 
      }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        tokens: state.tokens,
      }),
    }
  )
);