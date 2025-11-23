import { apiClient } from './api';
import { 
  AdCreate, 
  AdUpdate, 
  AdOut, 
  AdListOut, 
  AdFilter 
} from '../types/ad';

export const adsService = {
  async createAd(adData: AdCreate): Promise<AdOut> {
    return apiClient.post<AdOut>('/ads', adData);
  },

  async getAd(adId: string): Promise<AdOut> {
    return apiClient.get<AdOut>(`/ads/${adId}`);
  },

  async updateAd(adId: string, updateData: AdUpdate): Promise<AdOut> {
    return apiClient.patch<AdOut>(`/ads/${adId}`, updateData);
  },

  async deleteAd(adId: string): Promise<void> {
    return apiClient.delete(`/ads/${adId}`);
  },

  async getAds(filters: AdFilter): Promise<AdListOut> {
    const params = new URLSearchParams();
    
    if (filters.category) params.append('category', filters.category);
    if (filters.level) params.append('level', filters.level);
    if (filters.format) params.append('format', filters.format);
    if (filters.q) params.append('q', filters.q);
    if (filters.sort) params.append('sort', filters.sort);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());

    return apiClient.get<AdListOut>(`/ads?${params.toString()}`);
  },

  async getMyAds(): Promise<AdOut[]> {
    return apiClient.get<AdOut[]>('/ads/my/ads');
  }
};