import { ChatMessage } from './agent.models';

export interface SessionSummary {
  id: string;
  title: string | null;
  pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail {
  id: string;
  title: string | null;
  pinned: boolean;
  created_at: string;
  updated_at: string;
  messages: {
    id: number;
    session_id: string;
    role: 'user' | 'assistant' | 'tool';
    content: string;
    tool_calls: any;
    tool_call_id: string | null;
    timestamp: string;
  }[];
}

export function toChatMessage(msg: SessionDetail['messages'][0]): ChatMessage {
  return {
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
    timestamp: new Date(msg.timestamp),
  };
}
