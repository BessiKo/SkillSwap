import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/auth';
import { usersService } from '../services/users';
import { AuthState } from '../types/auth';

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    tokens: { accessToken: null },
    loading: true,
  });

  const login = useCallback(async (phone: string, code: string) => {
    try {
      const response = await authService.verifyCode(phone, code);
      const user = await usersService.getCurrentUser();
      
      setAuthState({
        isAuthenticated: true,
        user,
        tokens: { accessToken: response.access_token },
        loading: false,
      });
      
      return { success: true, isNewUser: response.is_new_user };
    } catch (error) {
      setAuthState(prev => ({ ...prev, loading: false }));
      return { success: false, error: (error as Error).message };
    }
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setAuthState({
      isAuthenticated: false,
      user: null,
      tokens: { accessToken: null },
      loading: false,
    });
  }, []);

  const requestCode = useCallback(async (phone: string) => {
    return await authService.requestCode(phone);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!authState.isAuthenticated) return;
    
    try {
      const user = await usersService.getCurrentUser();
      setAuthState(prev => ({ ...prev, user }));
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  }, [authState.isAuthenticated]);

  useEffect(() => {
    const initAuth = async () => {
      const tokenValid = authService.isTokenValid();
      
      if (tokenValid) {
        try {
          const user = await usersService.getCurrentUser();
          setAuthState({
            isAuthenticated: true,
            user,
            tokens: { accessToken: localStorage.getItem('access_token') },
            loading: false,
          });
        } catch (error) {
          console.error('Failed to restore session:', error);
          await authService.logout();
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
      }
    };

    initAuth();
  }, []);

  return {
    ...authState,
    login,
    logout,
    requestCode,
    refreshUser,
  };
};