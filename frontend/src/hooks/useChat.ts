/**
 * useChat Hook - 管理聊天状态和 MCP 通信
 */

import { useCallback, useRef, useState } from 'react';
import type { Message } from '../types';
import { mcpClient } from '../services/mcpClient';
import { sendMessage as saveToDatabase } from '../services/api';

interface UseChatReturn {
  messages: Message[];
  isProcessing: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
  setMessages: (msgs: Message[]) => void;
  currentEmotion: string;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '你好呀！我是陈筱雪，欢迎回来~ ✨',
      timestamp: Date.now(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentEmotion, setCurrentEmotion] = useState('neutral');
  const historyRef = useRef<Array<{ role: string; content: string }>>([]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isProcessing) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);
    setError(null);

    try {
      const emotion = await mcpClient.analyzeEmotion(text);
      setCurrentEmotion(emotion.emotion);

      historyRef.current.push({ role: 'user', content: text });

      const response = await mcpClient.chat(text, historyRef.current);

      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response,
        emotion: emotion.emotion,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      historyRef.current.push({ role: 'assistant', content: response });

      saveToDatabase({
        message: text,
        history: historyRef.current.slice(0, -1),
      }).catch((err) => {
        console.warn('保存对话到数据库失败:', err);
      });
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : '未知错误';
      setError(errorMsg);

      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `抱歉，我遇到了一些问题：${errorMsg}`,
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: '你好呀！我是陈筱雪，欢迎回来~ ✨',
        timestamp: Date.now(),
      },
    ]);
    historyRef.current = [];
    setCurrentEmotion('neutral');
    setError(null);
  }, []);

  const setMessagesDirect = useCallback((msgs: Message[]) => {
    setMessages(msgs);
  }, []);

  return {
    messages,
    isProcessing,
    error,
    sendMessage,
    clearMessages,
    setMessages: setMessagesDirect,
    currentEmotion,
  };
}
