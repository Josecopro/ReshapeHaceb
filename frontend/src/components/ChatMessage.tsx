interface ChatMessageData {
  id: string;
  role: 'system' | 'assistant' | 'user';
  text: string;
  timestamp: number;
}

interface ChatMessageProps {
  message: ChatMessageData;
}

const LABELS: Record<string, string> = {
  system: 'Sistema',
  assistant: 'Asistente IA',
  user: 'Tú',
};

const ChatMessage = ({ message }: ChatMessageProps) => (
  <div className={`chat-msg chat-msg--${message.role}`}>
    <div className="chat-msg-accent" />
    <div className="chat-msg-body">
      <div className="chat-msg-header">
        <span className="chat-msg-role">{LABELS[message.role]}</span>
        <span className="chat-msg-time">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      <div className="chat-msg-text">{message.text}</div>
    </div>
  </div>
);

export default ChatMessage;
