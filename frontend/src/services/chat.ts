import { apiClient } from './api';
import { 
  ChatResponse, 
  MessageResponse, 
  MessageCreate 
} from '../types/chat';

export const chatService = {
  async respondToAd(adId: string): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>(`/chats/ads/${adId}/respond`);
  },

  async getMyChats(): Promise<ChatResponse[]> {
    return apiClient.get<ChatResponse[]>('/chats/chats');
  },

  async getChatMessages(chatId: number, limit: number = 50, offset: number = 0): Promise<MessageResponse[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    
    return apiClient.get<MessageResponse[]>(`/chats/chats/${chatId}/messages?${params}`);
  },

  async sendMessage(chatId: number, text: string): Promise<MessageResponse> {
    const data: MessageCreate = { chat_id: chatId, text };
    return apiClient.post<MessageResponse>(`/chats/chats/${chatId}/messages`, data);
  }
};