import { apiClient } from './api';
import {
  UserListOut,
  AdListAdminOut,
  AdminLogOut,
  AdminStatsOut,
  ChatAdminOut,
  DealAdminOut,
  MessageAdminOut,
  UserBanRequest,
  AdminActionRequest
} from '../types/admin';
import { UserRole, DealStatus, AdminActionType } from '../types';

export const adminService = {
  // Пользователи
  async getUsersList(params: {
    page?: number;
    page_size?: number;
    search?: string;
    role?: UserRole;
    is_active?: boolean;
  }): Promise<{ items: UserListOut[]; total: number; page: number; pages: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return apiClient.get(`/admin/users?${searchParams.toString()}`);
  },

  async banUser(userId: string, banData: UserBanRequest): Promise<any> {
    return apiClient.post(`/admin/users/${userId}/ban`, banData);
  },

  async unbanUser(userId: string, unbanData: AdminActionRequest): Promise<any> {
    return apiClient.post(`/admin/users/${userId}/unban`, unbanData);
  },

  // Объявления
  async getAdsList(params: {
    page?: number;
    page_size?: number;
    search?: string;
    category?: string;
    author_id?: string;
  }): Promise<{ items: AdListAdminOut[]; total: number; page: number; pages: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return apiClient.get(`/admin/ads?${searchParams.toString()}`);
  },

  async deleteAd(adId: string, deleteData: AdminActionRequest): Promise<void> {
    return apiClient.post(`/admin/ads/${adId}`, deleteData);
  },

  // Чаты
  async getChatsList(params: {
    page?: number;
    page_size?: number;
    ad_id?: string;
    user_id?: string;
  }): Promise<{ items: ChatAdminOut[]; total: number; page: number; pages: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return apiClient.get(`/admin/chats?${searchParams.toString()}`);
  },

  async getChatMessages(chatId: number): Promise<MessageAdminOut[]> {
    return apiClient.get(`/admin/chats/${chatId}/messages`);
  },

  async deleteChat(chatId: number, deleteData: AdminActionRequest): Promise<void> {
    return apiClient.post(`/admin/chats/${chatId}`, deleteData);
  },

  // Сделки
  async getDealsList(params: {
    page?: number;
    page_size?: number;
    status?: DealStatus;
    user_id?: string;
  }): Promise<{ items: DealAdminOut[]; total: number; page: number; pages: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return apiClient.get(`/admin/deals?${searchParams.toString()}`);
  },

  async cancelDeal(dealId: number, cancelData: AdminActionRequest): Promise<any> {
    return apiClient.post(`/admin/deals/${dealId}/cancel`, cancelData);
  },

  // Логи и статистика
  async getAdminLogs(params: {
    page?: number;
    page_size?: number;
    action_type?: AdminActionType;
    admin_id?: string;
  }): Promise<{ items: AdminLogOut[]; total: number; page: number; pages: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return apiClient.get(`/admin/logs?${searchParams.toString()}`);
  },

  async getAdminStats(): Promise<AdminStatsOut> {
    return apiClient.get('/admin/stats');
  }
};