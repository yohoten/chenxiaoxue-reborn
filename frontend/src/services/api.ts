/**
 * API 服务层 - 基于统一 HTTP 客户端
 */

import httpClient from './httpClient';
import type {
  ChatRequest,
  ChatResponse,
  EmotionResult,
  Conversation,
  ResourceFile,
  MCPTool,
  MCPResult,
  DreamAnalysis,
} from '../types';

const API_BASE = '/api';
const MCP_BASE = '/mcp';

// ── 聊天 ─────────────────────────────────────────────────

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const { data } = await httpClient.post<ChatResponse>(`${API_BASE}/chat/send`, req);
  return data;
}

export async function* sendMessageStream(req: ChatRequest): AsyncGenerator<string> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ...req, stream: true }),
  });

  if (!resp.ok) {
    throw new Error(`Stream API Error: ${resp.status}`);
  }

  const reader = resp.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        try {
          const parsed = JSON.parse(data);
          if (parsed.content) yield parsed.content;
        } catch {
          // SSE 格式错误，跳过
        }
      }
    }
  }
}

// ── 历史记录 ─────────────────────────────────────────────

export async function getChatHistory(
  limit = 50,
  offset = 0,
): Promise<{ items: Conversation[]; total: number }> {
  const { data } = await httpClient.get(`${API_BASE}/chat/history`, {
    params: { limit, offset },
  });
  return data;
}

export async function deleteChatHistory(id: number): Promise<void> {
  await httpClient.delete(`${API_BASE}/chat/history/${id}`);
}

export async function clearAllHistory(): Promise<void> {
  await httpClient.delete(`${API_BASE}/chat/history`);
}

// ── 情感分析 ─────────────────────────────────────────────

export async function analyzeEmotion(
  text: string,
  method = 'auto',
): Promise<EmotionResult> {
  const { data } = await httpClient.post<EmotionResult>(`${API_BASE}/emotion/analyze`, {
    text,
    method,
  });
  return data;
}

// ── 梦境解析 ─────────────────────────────────────────────

export async function analyzeDream(
  dreamText: string,
  useAI = true,
): Promise<import('../types').DreamRecord> {
  const { data } = await httpClient.post(`${API_BASE}/dream/analyze`, {
    dream_text: dreamText,
    use_ai: useAI,
  });
  return data;
}

export async function getDreamRecords(
  limit = 50, offset = 0, month?: string,
): Promise<import('../types').DreamListResponse> {
  const { data } = await httpClient.get(`${API_BASE}/dream/records`, {
    params: { limit, offset, ...(month ? { month } : {}) },
  });
  return data;
}

export async function getDreamMonths(): Promise<{ months: string[] }> {
  const { data } = await httpClient.get(`${API_BASE}/dream/months`);
  return data;
}

export async function getDreamStats(): Promise<import('../types').DreamStats> {
  const { data } = await httpClient.get(`${API_BASE}/dream/stats`);
  return data;
}

export async function deleteDreamRecord(id: number): Promise<void> {
  await httpClient.delete(`${API_BASE}/dream/records/${id}`);
}

export async function generateDreamCard(
  dreamText: string, symbols: Array<{ symbol: string }>,
): Promise<import('../types').DreamCardData> {
  const { data } = await httpClient.post(`${API_BASE}/dream/card`, {
    dream_text: dreamText,
    detected_symbols: symbols,
  });
  return data;
}

export async function generateDreamWorld(
  dreamText: string, symbols: Array<{ symbol: string }>,
): Promise<import('../types').DreamWorldData> {
  const { data } = await httpClient.post(`${API_BASE}/dream/world`, {
    dream_text: dreamText,
    detected_symbols: symbols,
  });
  return data;
}

export async function recommendSoundscape(
  symbols: string[], mood?: string,
): Promise<import('../types').SoundscapeData> {
  const { data } = await httpClient.post(`${API_BASE}/dream/soundscape`, {
    symbols,
    mood: mood || 'neutral',
  });
  return data;
}

export async function generateMessengerWorld(
  dreamText: string, symbols: Array<{ symbol: string }>,
): Promise<any> {
  const { data } = await httpClient.post(`${API_BASE}/dream/messenger/world`, {
    dream_text: dreamText,
    symbols,
  });
  return data;
}

export async function getDreamStarMap(): Promise<any> {
  const { data } = await httpClient.get(`${API_BASE}/dream/starmap`);
  return data;
}

export async function getDreamSquare(): Promise<{ items: any[]; total: number }> {
  const { data } = await httpClient.get(`${API_BASE}/dream/square`);
  return data;
}

export async function getSymbolEncyclopedia(
  category?: string,
): Promise<import('../types').SymbolListResponse> {
  const { data } = await httpClient.get(`${API_BASE}/dream/encyclopedia`, {
    params: category ? { category } : {},
  });
  return data;
}

// ── 资源 ─────────────────────────────────────────────────

export async function getBackgrounds(): Promise<{ backgrounds: ResourceFile[] }> {
  const { data } = await httpClient.get(`${API_BASE}/resources/backgrounds`);
  return data;
}

export async function getCharacters(): Promise<{ characters: ResourceFile[] }> {
  const { data } = await httpClient.get(`${API_BASE}/resources/characters`);
  return data;
}

export async function getStarMaps(): Promise<{ star_maps: ResourceFile[] }> {
  const { data } = await httpClient.get(`${API_BASE}/resources/star-maps`);
  return data;
}

// ── MCP ──────────────────────────────────────────────────

export async function getMCPInfo(): Promise<{
  name: string;
  version: string;
  tools_count: number;
}> {
  const { data } = await httpClient.get(`${MCP_BASE}/info`);
  return data;
}

export async function listMCPTools(): Promise<{ tools: MCPTool[] }> {
  const { data } = await httpClient.get(`${MCP_BASE}/tools`);
  return data;
}

export async function executeMCPTool(
  name: string,
  arguments_: Record<string, unknown>,
): Promise<MCPResult> {
  const { data } = await httpClient.post<MCPResult>(`${MCP_BASE}/execute`, {
    name,
    arguments: arguments_,
  });
  return data;
}

// ── Humanizer ───────────────────────────────────────────

export async function analyzeHumanizer(text: string): Promise<unknown> {
  const { data } = await httpClient.post(`${API_BASE}/humanizer/analyze`, { text });
  return data;
}

export async function humanizeText(text: string): Promise<unknown> {
  const { data } = await httpClient.post(`${API_BASE}/humanizer/humanize`, { text });
  return data;
}

// ── 协作 ─────────────────────────────────────────────────

export async function sendCollaborationChat(
  messages: Array<{ role: string; content: string }>,
  useCollaboration: boolean,
): Promise<unknown> {
  const { data } = await httpClient.post(`${API_BASE}/chat`, {
    messages,
    use_collaboration: useCollaboration,
  });
  return data;
}

// ── 外部 MCP ─────────────────────────────────────────────

export async function getExternalMCPServers(): Promise<unknown> {
  const { data } = await httpClient.get(`${MCP_BASE}/external`);
  return data;
}
