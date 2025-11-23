import { apiClient } from './api';
import { UserProfileOut, UserUpdate, UserProfileGamifiedOut } from '../types/user';

export const usersService = {
  async getCurrentUser(): Promise<UserProfileOut> {
    return apiClient.get<UserProfileOut>('/users/me');
  },

  async updateCurrentUser(updateData: UserUpdate): Promise<UserProfileOut> {
    return apiClient.patch<UserProfileOut>('/users/me', updateData);
  },

  async getUserProfile(userId: string): Promise<UserProfileGamifiedOut> {
    return apiClient.get<UserProfileGamifiedOut>(`/gamification/profile/${userId}`);
  },

  async getMyProfileGamified(): Promise<UserProfileGamifiedOut> {
    return apiClient.get<UserProfileGamifiedOut>('/gamification/my/profile');
  }
};