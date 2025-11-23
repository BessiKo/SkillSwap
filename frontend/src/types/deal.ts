import { DealStatus } from './index';

export interface DealBase {
  proposed_skill?: string;
  proposed_time?: string;
  proposed_place?: string;
}

export interface DealCreate extends DealBase {
  chat_id: number;
}

export interface DealUpdate {
  status?: DealStatus;
  proposed_skill?: string;
  proposed_time?: string;
  proposed_place?: string;
}

export interface DealStatusLogOut {
  id: number;
  old_status?: DealStatus;
  new_status: DealStatus;
  changed_by_id: string;
  reason?: string;
  created_at: string;
  changed_by_name: string;
}

export interface DealOut {
  id: number;
  chat_id: number;
  status: DealStatus;
  student_id: string;
  teacher_id: string;
  proposed_skill?: string;
  proposed_time?: string;
  proposed_place?: string;
  created_at: string;
  updated_at?: string;
  status_logs: DealStatusLogOut[];
  student_name: string;
  teacher_name: string;
}

export interface DealStatusUpdate {
  status: DealStatus;
  reason?: string;
}

export interface DealProposal {
  skill: string;
  time: string;
  place: string;
}

export interface WebSocketDealMessage {
  type: string;
  chat_id: number;
  user_id: string;
  data: Record<string, any>;
}