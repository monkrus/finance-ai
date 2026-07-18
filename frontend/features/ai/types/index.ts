// AI Copilot Types

export interface ChatSession {
  id: string;
  title: string;
  updatedAt: string;
  folder?: string;
  pinned: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string; // Markdown
  timestamp: string;
  status: 'streaming' | 'complete' | 'error';
  citations?: Citation[];
  toolCalls?: ToolCall[];
  inlineData?: any; // Charts, Cards, etc.
}

export interface Citation {
  id: string;
  title: string;
  source: string;
  url?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed';
  durationMs?: number;
  input?: any;
  result?: any;
}

export interface SuggestedPrompt {
  id: string;
  title: string;
  description: string;
  prompt: string;
  category: 'Portfolio' | 'Market' | 'Wealth' | 'General';
}

export interface ActiveContext {
  portfolio: boolean;
  news: boolean;
  market: boolean;
  wealth: boolean;
  notifications: boolean;
}

export interface ChartIntent {
  type: 'line' | 'area' | 'donut' | 'bar';
  title: string;
  data: any[];
  xAxisKey?: string;
  seriesKey?: string;
}
