import { BadgeType } from './index';

export interface BadgeCreate {
  name: string;
  type: BadgeType;
  description: string;
  icon: string;
}

export interface BadgeOut {
  id: number;
  name: string;
  type: BadgeType;
  description: string;
  icon: string;
}

export interface ReviewCreate {
  target_user_id: string;
  deal_id: number;
  rating: number;
  text?: string;
}

export interface ReviewOut {
  id: number;
  author_id: string;
  target_user_id: string;
  deal_id: number;
  rating: number;
  text?: string;
  created_at: string;
  author_name: string;
  author_avatar?: string;
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

export interface LevelProgressOut {
  current_level: number;
  current_exp: number;
  next_level_exp: number;
  progress_percentage: number;
}

export interface LeaderboardUserOut {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  university: string;
  reputation: number;
  level: number;
  position: number;
}

export interface GlobalStatsOut {
  total_users: number;
  total_exchanges: number;
  total_reviews: number;
  average_rating: number;
  most_popular_category: string;
  top_university: string;
  active_this_week: number;
  new_users_today: number;
}

export interface AchievementOut {
  id: number;
  name: string;
  description: string;
  unlocked_at?: string;
  icon: string;
}

export interface NextAchievementOut {
  id: number;
  name: string;
  description: string;
  progress: number;
  required: number;
  progress_percentage: number;
}

export interface UserAchievementsOut {
  user_id: string;
  unlocked_achievements: AchievementOut[];
  next_achievements: NextAchievementOut[];
}

export interface BadgeAwardResponse {
  message: string;
  user_id: string;
  badge_id: number;
  badge_name: string;
}

export interface DetailedStatsOut {
  total_badges: number;
  users_with_badges: number;
  badge_distribution_rate: number;
  most_awarded_badges: Array<Record<string, any>>;
}