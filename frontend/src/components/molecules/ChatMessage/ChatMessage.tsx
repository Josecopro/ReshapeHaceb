import type { ChatMessageData } from '@/types';
import './ChatMessage.scss';

const LABELS: Record<string, string> = {
  system: 'Sistema',
  assistant: 'Asistente IA',
  user: 'Tú',
};

interface ChatMessageProps {
  message: ChatMessageData;
}

const ChatMessage = ({ message }: ChatMessageProps) => (
  <div className={`chat-msg chat-msg--${message.role}`}>
    <div className="chat-msg__accent" />
    <div className="chat-msg__body">
      <div className="chat-msg__header">
        <span className="chat-msg__role">{LABELS[message.role]}</span>
        <span className="chat-msg__time">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      <div className="chat-msg__text">{message.text}</div>
    </div>
  </div>
);

export default ChatMessage;
