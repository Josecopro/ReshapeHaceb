export interface ChatMessageData {
  id: string;
  role: 'system' | 'assistant' | 'user';
  text: string;
  timestamp: number;
}
