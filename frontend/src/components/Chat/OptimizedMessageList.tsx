// 优化的消息列表组件 - 支持虚拟滚动和分页加载
// 位置: frontend/src/components/Chat/OptimizedMessageList.tsx

import React, { useRef, useEffect, useState, useMemo, useCallback, type JSX } from 'react';
import { ChatBubble } from './ChatBubble';
import { Message, Conversation } from '../../types';
import { getChatHistory } from '../../services/api';

interface OptimizedMessageListProps {
  messages: Message[];
  typewriterEffect?: boolean;
  glassEffect?: boolean;
  isProcessing?: boolean;
}

/**
 * 优化的消息列表组件
 * 特性：
 * 1. 虚拟滚动 - 只渲染可见区域的消息
 * 2.  memoization - 避免不必要的重渲染
 * 3. 分页加载 - 滚动到顶部时自动加载历史消息
 */
export const OptimizedMessageList: React.FC<OptimizedMessageListProps> = React.memo(({
  messages,
  typewriterEffect = false,
  glassEffect = false,
  isProcessing = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 50 });
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [loadedHistory, setLoadedHistory] = useState<Message[]>([]);
  const [historyOffset, setHistoryOffset] = useState(0);
  const [hasMoreHistory, setHasMoreHistory] = useState(true);
  const prevScrollHeightRef = useRef(0);
  const PAGE_SIZE = 20;

  // 合并当前消息和历史消息
  const allMessages = useMemo(() => {
    return [...loadedHistory, ...messages];
  }, [loadedHistory, messages]);

  // 配置参数
  const ITEM_HEIGHT = 150; // 预估每条消息的高度
  const BUFFER_COUNT = 10; // 缓冲区消息数量

  // 计算可见范围
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      const viewportHeight = container.clientHeight;
      
      const start = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_COUNT);
      const end = Math.min(
        allMessages.length,
        Math.ceil((scrollTop + viewportHeight) / ITEM_HEIGHT) + BUFFER_COUNT
      );

      setVisibleRange({ start, end });
    };

    container.addEventListener('scroll', handleScroll);
    handleScroll(); // 初始化

    return () => container.removeEventListener('scroll', handleScroll);
  }, [allMessages.length]);

  // 自动滚动到底部（新消息时），仅当用户不在查看历史时
  useEffect(() => {
    const container = containerRef.current;
    if (container && visibleRange.end >= allMessages.length - 1) {
      requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
      });
    }
  }, [messages.length]);

  // 将 Conversation 转换为 Message
  const conversationToMessage = useCallback((conv: Conversation): Message => ({
    id: `history-${conv.id}`,
    role: 'user' as const,
    content: conv.user_input,
    timestamp: new Date(conv.created_at).getTime(),
  }), []);

  const conversationToAssistantMessage = useCallback((conv: Conversation): Message => ({
    id: `history-${conv.id}-response`,
    role: 'assistant' as const,
    content: conv.assistant_response,
    modelName: conv.model_name,
    timestamp: new Date(conv.created_at).getTime() + 1,
  }), []);

  // 加载更多历史消息 - 真实 API 调用
  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMoreHistory) return;
    
    setIsLoadingMore(true);
    
    try {
      const result = await getChatHistory(PAGE_SIZE, historyOffset);
      
      if (result.items.length === 0) {
        setHasMoreHistory(false);
        return;
      }
      
      // 记录加载前的滚动高度，用于维持滚动位置
      if (containerRef.current) {
        prevScrollHeightRef.current = containerRef.current.scrollHeight;
      }
      
      // 将后端对话记录转换为消息格式
      const historyMessages: Message[] = [];
      for (const conv of result.items) {
        historyMessages.push(conversationToMessage(conv));
        historyMessages.push(conversationToAssistantMessage(conv));
      }
      
      // 历史消息按时间正序排列，反向追加到前面
      setLoadedHistory(prev => [...historyMessages.reverse(), ...prev]);
      setHistoryOffset(prev => prev + result.items.length);
      
      // 如果返回的数量少于请求数量，说明没有更多了
      if (result.items.length < PAGE_SIZE) {
        setHasMoreHistory(false);
      }
      
      // 维持滚动位置：新消息被插入到顶部后，调整 scrollTop
      requestAnimationFrame(() => {
        if (containerRef.current) {
          const newScrollHeight = containerRef.current.scrollHeight;
          const heightDiff = newScrollHeight - prevScrollHeightRef.current;
          containerRef.current.scrollTop = heightDiff;
        }
      });
    } catch (error) {
      console.warn('加载历史消息失败:', error);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, hasMoreHistory, historyOffset, conversationToMessage, conversationToAssistantMessage]);

  // 记忆化渲染的消息
  const visibleMessages = useMemo(() => {
    return allMessages.slice(visibleRange.start, visibleRange.end);
  }, [allMessages, visibleRange]);

  // 计算占位高度
  const topPadding = visibleRange.start * ITEM_HEIGHT;
  const bottomPadding = (allMessages.length - visibleRange.end) * ITEM_HEIGHT;

  // 滚动到顶部时自动加载更多历史消息
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (container.scrollTop < 100 && !isLoadingMore && hasMoreHistory) {
        loadMore();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [isLoadingMore, hasMoreHistory, loadMore]);

  return (
    <div
      ref={containerRef}
      className={`message-list ${glassEffect ? 'glass-effect' : ''}`}
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        scrollBehavior: 'smooth',
      }}
    >
      {/* 顶部占位 */}
      <div style={{ height: topPadding }} />

      {/* 可见消息 */}
      {visibleMessages.map((message, index) => (
        <ChatBubble
          key={message.id || `msg-${visibleRange.start + index}`}
          message={message}
          glassEffect={glassEffect}
          typewriterEffect={typewriterEffect && message.role === 'assistant'}
        />
      ))}

      {/* 底部占位 */}
      <div style={{ height: bottomPadding }} />

      {/* AI 正在处理指示器 */}
      {isProcessing && (
        <div className="loading-indicator" style={{ padding: '15px 0' }}>
          <span>Chen筱雪正在输入</span>
          <span className="loading-dots" />
        </div>
      )}

      {/* 加载更多历史消息提示 */}
      {isLoadingMore && (
        <div style={{
          textAlign: 'center',
          padding: '10px',
          color: '#888',
          fontSize: '12px',
        }}>
          <span className="loading-dots" /> 加载历史消息...
        </div>
      )}

      {/* 没有更多历史消息提示 */}
      {!hasMoreHistory && loadedHistory.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '8px',
          color: '#666',
          fontSize: '11px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        }}>
          ─── 已加载全部历史消息 ───
        </div>
      )}
    </div>
  );
});

OptimizedMessageList.displayName = 'OptimizedMessageList';