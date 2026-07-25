import { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';

export interface ChatMessageData {
  id: string;
  role: 'system' | 'assistant' | 'user';
  text: string;
  timestamp: number;
}

interface AgentChatProps {
  messages: ChatMessageData[];
  open: boolean;
  onToggle: () => void;
}

const AgentChat = ({ messages, open, onToggle }: AgentChatProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <>
      <button
        className={`chat-toggle${open ? ' chat-toggle--open' : ''}`}
        onClick={onToggle}
        title={open ? 'Cerrar chat' : 'Abrir chat'}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          className={`chat-toggle-chevron${open ? ' chat-toggle-chevron--open' : ''}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>

      <aside className={`chat-sidebar${open ? ' chat-sidebar--open' : ''}`}>
        <div className="chat-header">
          <div className="chat-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <span>Chat del Agente IA</span>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-bar">
          <input
            className="chat-input"
            type="text"
            placeholder="Escribe un mensaje..."
            disabled
          />
          <button className="chat-send-btn" disabled>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </aside>
    </>
  );
};

export default AgentChat;
