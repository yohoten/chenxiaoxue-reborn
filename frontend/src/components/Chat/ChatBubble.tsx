/**
 * 聊天气泡 — 支持打字机效果（全局 rAF 调度器，零独立 setInterval）
 */

import { useState, useEffect, useRef } from 'react';
import type { Message } from '../../types';
import { typewriterScheduler } from '../../hooks/typewriterScheduler';

interface ChatBubbleProps {
  message: Message;
  glassEffect?: boolean;
  typewriterEffect?: boolean;
}

function smartTime(ts: number): string {
  const d = new Date(ts);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const isYesterday = d.toDateString() === yesterday.toDateString();
  if (isToday) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  if (isYesterday) return `昨天 ${d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
  return `${d.getMonth() + 1}-${d.getDate()}`;
}

export function ChatBubble({ message, glassEffect = false, typewriterEffect = false }: ChatBubbleProps) {
  const isUser = message.role === 'user';
  const [displayedContent, setDisplayedContent] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const idxRef = useRef(0);

  useEffect(() => {
    if (isUser || !typewriterEffect) {
      setDisplayedContent(message.content);
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    setDisplayedContent('');
    idxRef.current = 0;
    const content = message.content;

    const tick = (): boolean => {
      if (idxRef.current < content.length) {
        idxRef.current++;
        setDisplayedContent(content.substring(0, idxRef.current));
        return false;
      }
      setIsTyping(false);
      return true; // 已完成，调度器自动移除
    };

    typewriterScheduler.add(tick);
    return () => typewriterScheduler.remove(tick);
  }, [message.content, isUser, typewriterEffect]);

  return (
    <div
      className={`message-bubble message-bubble--${message.role} ${glassEffect ? 'glass-effect' : ''}`}
      style={{ alignSelf: isUser ? 'flex-end' : 'flex-start' }}
    >
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: 4, fontSize: 10, opacity: 0.6,
      }}>
        <span>{isUser ? '👤 你' : '🤖 ChenXiaoxue'}</span>
        <span>{smartTime(message.timestamp || Date.now())}</span>
      </div>

      <div
        className={isTyping && typewriterEffect && !isUser ? 'typing-cursor' : ''}
        style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontFamily: 'var(--font-readable)' }}
      >
        {displayedContent}
      </div>

      {message.modelName && !isUser && (
        <div style={{
          fontSize: 10, marginTop: 8, opacity: 0.5,
          borderTop: '1px solid rgba(42, 59, 90, 0.3)', paddingTop: 4,
        }}>
          via {message.modelName}
        </div>
      )}
    </div>
  );
}
