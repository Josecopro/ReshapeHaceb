'use client';

import { useRef, useEffect } from 'react';
import { Icon } from '@/components/atoms';
import { ChatMessage } from '@/components/molecules';
import type { ChatMessageData } from '@/types';
import './ChatSidebar.scss';

interface ChatSidebarProps {
  messages: ChatMessageData[];
  open: boolean;
  onToggle: () => void;
}

const ChatSidebar = ({ messages, open, onToggle }: ChatSidebarProps) => {
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
            placeholder="Escribe un mensaje..."
            disabled
          />
          <button className="chat-sidebar__send" disabled>
            <Icon name="send" size={16} />
          </button>
        </div>
      </aside>
    </>
  );
};

export default ChatSidebar;
