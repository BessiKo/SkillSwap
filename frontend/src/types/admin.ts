import { AdminActionType, DealStatus } from './index';
import { UserProfileOut } from './user';
import { AdOut } from './ad'; // Исправлен импорт

export interface UserBanRequest {
  reason?: string;
  details?: string;
}

export interface AdminActionRequest {
  reason?: string;
  details?: string;
}

export interface AdminLogOut {
  id: number;
  admin_id: string;
  action_type: AdminActionType;
  target_user_id?: string;
  target_ad_id?: string;
  target_chat_id?: number;
  target_deal_id?: number;
  reason?: string;
  details?: string;
  created_at: string;
  admin?: UserProfileOut;
  target_user?: UserProfileOut;
  target_ad?: AdOut;
}

export interface MessageAdminOut {
  id: number;
  chat_id: number;
  sender: UserProfileOut;
  text: string;
  created_at: string;
  read_at?: string;
}

export interface ChatAdminOut {
  id: number;
  ad: AdOut;
  user1: UserProfileOut;
  user2: UserProfileOut;
  created_at: string;
  messages: MessageAdminOut[];
  has_deal: boolean;
}

export interface DealAdminOut {
  id: number;
  chat_id: number;
  status: DealStatus;
  student: UserProfileOut;
  teacher: UserProfileOut;
  proposed_skill?: string;
  proposed_time?: string;
  proposed_place?: string;
  created_at: string;
  updated_at?: string;
}

export interface AdminStatsOut {
  total_users: number;
  total_ads: number;
  total_chats: number;
  total_deals: number;
  active_users: number;
  active_ads: number;
  banned_users: number;
  recent_actions: AdminLogOut[];
}

export interface UserListOut {
  id: string;
  phone: string;
  role: string;
  is_active: boolean;
  created_at: string;
  profile?: UserProfileOut;
  ads_count: number;
  chats_count: number;
  deals_count: number;
}

export interface AdListAdminOut {
  id: string;
  title: string;
  category: string;
  level: string;
  format: string;
  created_at: string;
  author: UserProfileOut;
  is_active: boolean;
  chats_count: number;
}