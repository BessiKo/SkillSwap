import { apiClient } from './api';
import {
  ReviewCreate,
  ReviewOut,
  LevelProgressOut,
  LeaderboardUserOut,
  BadgeOut,
  GlobalStatsOut,
  UserAchievementsOut,
  BadgeAwardResponse,
  DetailedStatsOut
} from '../types/gamification';

export const gamificationService = {
  async createReview(reviewData: ReviewCreate): Promise<ReviewOut> {
    return apiClient.post<ReviewOut>('/gamification/reviews', reviewData);
  },

  async getLeaderboard(limit: number = 50): Promise<LeaderboardUserOut[]> {
    return apiClient.get<LeaderboardUserOut[]>(`/gamification/leaderboard?limit=${limit}`);
  },

  async getLevelProgress(): Promise<LevelProgressOut> {
    return apiClient.get<LevelProgressOut>('/gamification/level-progress');
  },

  async getUserReviews(userId: string, limit: number = 20, offset: number = 0): Promise<ReviewOut[]> {
    return apiClient.get<ReviewOut[]>(`/gamification/users/${userId}/reviews?limit=${limit}&offset=${offset}`);
  },

  async getAllBadges(): Promise<BadgeOut[]> {
    return apiClient.get<BadgeOut[]>('/gamification/badges');
  },

  async getGlobalStats(): Promise<GlobalStatsOut> {
    return apiClient.get<GlobalStatsOut>('/gamification/stats/global');
  },

  async getUnlockedAchievements(): Promise<UserAchievementsOut> {
    return apiClient.get<UserAchievementsOut>('/gamification/achievements/unlocked');
  },

  // Админ методы
  async createBadge(badgeData: any): Promise<BadgeOut> {
    return apiClient.post<BadgeOut>('/gamification/admin/badges', badgeData);
  },

  async awardBadgeToUser(userId: string, badgeId: number): Promise<BadgeAwardResponse> {
    return apiClient.post<BadgeAwardResponse>(`/gamification/admin/users/${userId}/award-badge/${badgeId}`);
  },

  async getDetailedStats(): Promise<DetailedStatsOut> {
    return apiClient.get<DetailedStatsOut>('/gamification/admin/stats/detailed');
  }
};