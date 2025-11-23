import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export function useAuth() {
  const store = useAuthStore();

  useEffect(() => {
    store.checkAuth();
  }, []);

  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    isNewUser: store.isNewUser,
    isAdmin: store.user?.role === 'admin',
    requestCode: store.requestCode,
    verifyCode: store.verifyCode,
    logout: store.logout,
    clearNewUserFlag: store.clearNewUserFlag,
  };
}