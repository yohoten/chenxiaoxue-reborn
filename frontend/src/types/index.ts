/** 聊天消息 */
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  emotion?: string;
  modelName?: string;
  timestamp: number;
}

/** 聊天请求 */
export interface ChatRequest {
  message: string;
  history?: Array<{ role: string; content: string }>;
  model?: string;
  stream?: boolean;
  temperature?: number;
}

/** 聊天响应 */
export interface ChatResponse {
  response: string;
  model_name: string;
  provider: string;
  emotion: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  latency_ms: number;
}

/** 情感分析结果 */
export interface EmotionResult {
  emotion: string;
  confidence: number;
  emoji: string;
  details?: Record<string, unknown>;
}

/** 对话记录 */
export interface Conversation {
  id: number;
  user_input: string;
  assistant_response: string;
  intent?: string;
  emotion?: string;
  model_name?: string;
  tokens_used?: number;
  created_at: string;
}

/** MCP 工具定义 */
export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

/** MCP 执行结果 */
export interface MCPResult {
  isError: boolean;
  content: Array<{ type: string; text: string }>;
}

/** 资源文件信息 */
export interface ResourceFile {
  name: string;
  path: string;
  type: string;
  is_animated: boolean;
}

/** 梦境符号解析 */
export interface DreamSymbol {
  symbol: string;
  category?: string;
  emoji?: string;
  interpretations: string[];
}

/** 梦境分析结果 */
export interface DreamAnalysis {
  dream_text: string;
  detected_symbols: DreamSymbol[];
  traditional_analysis: string;
  symbol_count: number;
  analysis_type: 'traditional' | 'ai_enhanced';
}

/** 梦境记录 */
export interface DreamRecord {
  id: number;
  user_id: number;
  dream_text: string;
  emotion?: string;
  detected_symbols: DreamSymbol[];
  traditional_analysis?: string;
  ai_analysis?: string;
  analysis_type: string;
  dream_date: string;
  created_at: string;
}

/** 梦境列表响应 */
export interface DreamListResponse {
  items: DreamRecord[];
  total: number;
}

/** 梦境统计 */
export interface DreamStats {
  total_dreams: number;
  monthly_dreams: number;
  top_symbols: Array<{ symbol: string; count: number }>;
}

/** 符号百科条目 */
export interface SymbolEncyclopediaItem {
  symbol: string;
  category: string;
  emoji: string;
  interpretations: string[];
  related_symbols: string[];
}

/** 符号百科响应 */
export interface SymbolListResponse {
  symbols: SymbolEncyclopediaItem[];
  categories: string[];
  total: number;
}

/** 梦境卡片数据 */
export interface DreamCardData {
  title: string;
  mood: string;
  mood_emoji: string;
  poetic_line: string;
  symbols_summary: string;
  suggested_music: string;
  color_theme: string;
}

/** 音景推荐数据 */
export interface SoundscapeData {
  music_type: string;
  description: string;
  color_palette: string[];
  bpm_range: string;
}

/** 梦境世界 3D 数据 */
export interface DreamWorldData {
  planet: { radius: number; segments: number };
  colors: { land: string; water: string; sky: string };
  mood: string;
  objects: Array<{
    id: number;
    symbol: string;
    emoji: string;
    interpretation: string;
    position: [number, number, number];
    size: number;
  }>;
  symbol_count: number;
}

/** 应用配置 */
export interface AppConfig {
  backgroundIndex: number;
  theme: string;
  fontSize: number;
  language: string;
}