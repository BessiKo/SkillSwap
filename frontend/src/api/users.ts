import { apiClient } from './client';
import type { User, ProfileUpdateData } from '../types';

/**
 * API методы для работы с данными пользователя и профиля.
 */
export const usersApi = {
  /**
   * Получает данные текущего аутентифицированного пользователя.
   */
  getMe: (): Promise<User> => {
    // Для этого запроса требуется access token (по умолчанию включен в apiClient)
    return apiClient.get('/users/me');
  },

  /**
   * Обновляет профиль текущего пользователя.
   */
  updateProfile: (data: ProfileUpdateData): Promise<User> => {
    return apiClient.patch('/users/me/profile', data);
  }
};