/**
 * MCP 客户端 - 封装与 MCP Server 的通信
 * 
 * 遵循 MCP (Model Context Protocol) 规范
 * 提供 AI 模型工具调用能力
 */

import { executeMCPTool, listMCPTools } from './api';
import type { MCPTool, MCPResult } from '../types';

export class MCPClient {
  private tools: Map<string, MCPTool> = new Map();
  private initialized = false;

  /** 初始化 MCP 客户端 - 获取可用工具列表 */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      const { tools } = await listMCPTools();
      for (const tool of tools) {
        this.tools.set(tool.name, tool);
      }
      this.initialized = true;
      console.log(`[MCP] 已加载 ${tools.length} 个工具`);
    } catch (error) {
      console.error('[MCP] 初始化失败:', error);
      throw error;
    }
  }

  /** 获取所有可用工具 */
  getAvailableTools(): MCPTool[] {
    return Array.from(this.tools.values());
  }

  /** 检查工具是否存在 */
  hasTool(name: string): boolean {
    return this.tools.has(name);
  }

  /** 调用 AI 聊天工具 */
  async chat(
    message: string,
    history?: Array<{ role: string; content: string }>
  ): Promise<string> {
    const messages = [
      {
        role: 'system',
        content:
          '你是一个名为"陈筱雪"的像素风格AI助手。' +
          '你的性格温柔、友善、略带俏皮。' +
          '你会根据用户的情感状态调整回复风格。' +
          '请用中文回复，保持像素风格的可爱感。',
      },
      ...(history || []),
      { role: 'user', content: message },
    ];

    const result = await this.executeTool('chat_completion', {
      messages,
    });

    if (result.isError) {
      throw new Error(result.content[0]?.text || 'MCP 调用失败');
    }

    try {
      const data = JSON.parse(result.content[0]?.text || '{}');
      return data.response || '抱歉，我没有理解你的意思。';
    } catch {
      return result.content[0]?.text || '抱歉，出了点问题。';
    }
  }

  /** 分析情感 */
  async analyzeEmotion(text: string): Promise<{
    emotion: string;
    emoji: string;
    confidence: number;
  }> {
    const result = await this.executeTool('analyze_emotion', { text });

    if (result.isError) {
      return { emotion: 'neutral', emoji: '😐', confidence: 0.5 };
    }

    try {
      return JSON.parse(result.content[0]?.text || '{}');
    } catch {
      return { emotion: 'neutral', emoji: '😐', confidence: 0.5 };
    }
  }

  /** 翻译文本 */
  async translate(
    text: string,
    targetLang: string
  ): Promise<string> {
    const result = await this.executeTool('translate_text', {
      text,
      target_lang: targetLang,
    });

    if (result.isError) {
      throw new Error(result.content[0]?.text);
    }

    try {
      const data = JSON.parse(result.content[0]?.text || '{}');
      return data.translated_text || text;
    } catch {
      return text;
    }
  }

  /** 通用工具执行 */
  private async executeTool(
    name: string,
    args: Record<string, unknown>
  ): Promise<MCPResult> {
    if (!this.hasTool(name)) {
      return {
        isError: true,
        content: [{ type: 'text', text: `Tool '${name}' not found` }],
      };
    }

    return executeMCPTool(name, args);
  }
}

/** 全局 MCP 客户端单例 */
export const mcpClient = new MCPClient();
