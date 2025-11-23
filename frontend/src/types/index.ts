export type UserRole = 'student' | 'admin';

export type BadgeType = 
  | 'newcomer' 
  | 'first_exchange' 
  | 'popular' 
  | 'top_rated' 
  | 'mentor' 
  | 'expert';

export interface Badge {
  id: number;
  name: string;
  type: BadgeType;
  description: string;
  icon: string;
}

export interface UserProfile {
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  bio: string;
  university: string;
  faculty: string;
  year: number | null;
  rating: number;
  total_ratings: number;
  exchanges_completed: number;
  reviews_received: number;
}

export interface User {
  id: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  profile: UserProfile | null;
  badges: Badge[];
}

export interface UserPublicProfile {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  bio: string;
  university: string;
  faculty: string;
  year: number | null;
  rating: number;
  total_ratings: number;
  exchanges_completed: number;
  reviews_received: number;
  badges: Badge[];
}

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  bio?: string;
  university?: string;
  faculty?: string;
  year?: number | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  is_new_user: boolean;
}

export interface CodeRequestResponse {
  message: string;
  expires_in: number;
  debug_code?: string;
}

export interface ApiError {
  detail: string;
}