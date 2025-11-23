export interface ChatBase {
  ad_id: string;
  user2_id: string;
}

export interface ChatCreate extends ChatBase {}

export interface ChatResponse {
  id: number;
  ad_id: string;
  user1_id: string;
  user2_id: string;
  created_at: string;
  last_message?: MessageResponse;
  unread_count: number;
}

export interface MessageBase {
  text: string;
}

export interface MessageCreate extends MessageBase {
  chat_id: number;
}

export interface MessageResponse {
  id: number;
  chat_id: number;
  sender_id: string;
  text: string;
  created_at: string;
  read_at?: string;
  sender_name: string;
}

export interface WebSocketMessage {
  type: string;
  chat_id: number;
  sender_id: string;
  data: Record<string, any>;
}