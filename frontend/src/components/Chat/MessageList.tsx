/**
 * 消息列表组件
 * 显示聊天消息，支持打字机效果
 */

import { useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import type { Message } from '../../types';

interface MessageListProps {
  messages: Message[];
  isProcessing: boolean;
  glassEffect?: boolean;
  typewriterEffect?: boolean;
}

export function MessageList({
  messages,
  isProcessing,
  glassEffect = false,
  typewriterEffect = false,
}: MessageListProps) {
  const listRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="message-list" ref={listRef}>
      {messages.map((msg) => (
        <ChatBubble key={msg.id} message={msg} glassEffect={glassEffect} typewriterEffect={typewriterEffect} />
      ))}
      {isProcessing && (
        <div className="loading-indicator">
          <span>Chen筱雪正在输入</span>
          <span className="loading-dots" />
        </div>
      )}
    </div>
  );
}
