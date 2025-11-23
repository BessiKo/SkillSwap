import { BadgeType } from './index';
import { ReviewOut } from './gamification'; 

export interface BadgeOut {
  name: string;
  type: BadgeType;
  icon: string;
  description: string;
}

export interface UserProfileOut {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  bio: string;
  university: string;
  faculty: string;
  year?: number;
  rating: number;
  total_ratings: number;
  exchanges_completed: number;
  reviews_received: number;
  badges: BadgeOut[];
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  bio?: string;
  university?: string;
  faculty?: string;
  year?: number;
}

export interface UserStatsOut {
  reputation: number;
  exchanges_completed: number;
  total_ratings: number;
  average_rating: number;
  level: number;
  experience: number;
  next_level_exp: number;
  programming_exchanges: number;
  design_exchanges: number;
  languages_exchanges: number;
  math_exchanges: number;
  science_exchanges: number;
  business_exchanges: number;
  music_exchanges: number;
  sports_exchanges: number;
  other_exchanges: number;
}

export interface UserProfileGamifiedOut {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  university: string;
  faculty: string;
  year?: number;
  bio: string;
  stats: UserStatsOut;
  badges: BadgeOut[];
  reviews: ReviewOut[]; // Теперь используем правильный тип
}