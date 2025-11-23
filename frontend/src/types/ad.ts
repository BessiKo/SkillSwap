import { AdCategory, AdLevel, AdFormat } from './index';

export interface AuthorOut {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  rating: number;
}

export interface AdCreate {
  category: AdCategory;
  title: string;
  description: string;
  level: AdLevel;
  format: AdFormat;
}

export interface AdUpdate {
  category?: AdCategory;
  title?: string;
  description?: string;
  level?: AdLevel;
  format?: AdFormat;
}

export interface AdOut {
  id: string;
  author: AuthorOut;
  category: AdCategory;
  title: string;
  description: string;
  level: AdLevel;
  format: AdFormat;
  created_at: string;
  updated_at?: string;
}

export interface AdListOut {
  items: AdOut[];
  total: number;
  page: number;
  pages: number;
}

export interface AdFilter {
  category?: AdCategory;
  level?: AdLevel;
  format?: AdFormat;
  q?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}