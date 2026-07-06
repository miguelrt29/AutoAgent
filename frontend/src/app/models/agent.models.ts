export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface ToolCall {
  tool: string
  input: Record<string, any>
  timestamp: Date
}

export interface AgentEvent {
  type: 'tool_call' | 'text' | 'error' | 'done'
  tool?: string
  input?: Record<string, any>
  content?: string
  message?: string
}

export interface ChatSession {
  sessionId: string
  messages: ChatMessage[]
  toolCalls: ToolCall[]
  isStreaming: boolean
}
