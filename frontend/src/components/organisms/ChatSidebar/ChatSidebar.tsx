'use client';

import { useRef, useEffect, useState } from 'react';
import { Icon } from '@/components/atoms';
import { ChatMessage } from '@/components/molecules';
import type { ChatMessageData } from '@/types';
import './ChatSidebar.scss';

interface ChatSidebarProps {
  messages: ChatMessageData[];
  open: boolean;
  onToggle: () => void;
  onSendMessage?: (text: string) => void;
}

const ChatSidebar = ({ messages, open, onToggle, onSendMessage }: ChatSidebarProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState('');

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || !onSendMessage) return;
    onSendMessage(text);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <button
        className={`chat-toggle${open ? ' chat-toggle--open' : ''}`}
        onClick={onToggle}
        title={open ? 'Cerrar chat' : 'Abrir chat'}
      >
        <Icon
          name="chevron"
          size={16}
          className={`chat-toggle__chevron${open ? ' chat-toggle__chevron--open' : ''}`}
        />
      </button>

      <aside className={`chat-sidebar${open ? ' chat-sidebar--open' : ''}`}>
        <div className="chat-sidebar__header">
          <div className="chat-sidebar__title">
            <Icon name="chat" size={16} />
            <span>Chat del Agente IA</span>
          </div>
        </div>

        <div className="chat-sidebar__messages">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="chat-sidebar__input-bar">
          <input
            className="chat-sidebar__input"
            type="text"
            placeholder="Describe el problema técnico..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="chat-sidebar__send"
            disabled={!input.trim()}
            onClick={handleSend}
          >
            <Icon name="send" size={16} />
          </button>
        </div>
      </aside>
    </>
  );
};

export default ChatSidebar;
