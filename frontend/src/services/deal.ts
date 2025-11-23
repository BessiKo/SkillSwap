import { apiClient } from './api';
import { 
  DealOut, 
  DealProposal, 
  DealStatusUpdate,
  DealStatusLogOut 
} from '../types/deal';

export const dealService = {
  async proposeDeal(chatId: number, proposal: DealProposal): Promise<DealOut> {
    return apiClient.post<DealOut>(`/deals/chats/${chatId}/propose`, proposal);
  },

  async updateDealStatus(chatId: number, statusUpdate: DealStatusUpdate): Promise<DealOut> {
    return apiClient.patch<DealOut>(`/deals/chats/${chatId}/status`, statusUpdate);
  },

  async getChatDeal(chatId: number): Promise<DealOut> {
    return apiClient.get<DealOut>(`/deals/chats/${chatId}`);
  },

  async getMyDeals(): Promise<DealOut[]> {
    return apiClient.get<DealOut[]>('/deals/my');
  },

  async getDealLogs(dealId: number): Promise<DealStatusLogOut[]> {
    return apiClient.get<DealStatusLogOut[]>(`/deals/${dealId}/logs`);
  }
};