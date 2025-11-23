// Базовые типы
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

// Enums из бекенда
export enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  ADMIN = "admin"
}

export enum AdCategory {
  PROGRAMMING = "programming",
  DESIGN = "design",
  LANGUAGES = "languages",
  MATH = "math",
  SCIENCE = "science",
  BUSINESS = "business",
  MUSIC = "music",
  SPORTS = "sports",
  OTHER = "other"
}

export enum AdLevel {
  BEGINNER = "beginner",
  INTERMEDIATE = "intermediate",
  ADVANCED = "advanced"
}

export enum AdFormat {
  ONLINE = "online",
  OFFLINE = "offline",
  ANY = "any"
}

export enum DealStatus {
  PENDING = "pending",
  ACCEPTED = "accepted",
  REJECTED = "rejected",
  COMPLETED = "completed",
  CANCELLED = "cancelled"
}

export enum BadgeType {
  NEWCOMER = "newcomer",
  FIRST_EXCHANGE = "first_exchange",
  POPULAR = "popular",
  TOP_RATED = "top_rated",
  MENTOR = "mentor",
  EXPERT = "expert",
  CATEGORY_EXPERT = "category_expert"
}

export enum AdminActionType {
  USER_BANNED = "user_banned",
  USER_UNBANNED = "user_unbanned",
  AD_DELETED = "ad_deleted",
  AD_HIDDEN = "ad_hidden",
  AD_RESTORED = "ad_restored",
  CHAT_DELETED = "chat_deleted",
  DEAL_CANCELLED = "deal_cancelled",
  DEAL_MODIFIED = "deal_modified"
}
