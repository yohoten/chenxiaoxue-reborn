/**
 * 梦境空间 v2 — 集成梦境解析、日记、符号百科
 * 支持三个子标签: 解析 / 日记 / 百科
 */
import { useState } from 'react';
import { PixelButton } from '../Common/PixelButton';
import { DreamJournal } from './DreamJournal';
import { DreamCard } from './DreamCard';
import { SymbolEncyclopedia } from './SymbolEncyclopedia';
import { analyzeDream } from '../../services/api';
import type { DreamRecord } from '../../types';
import { DreamWorld } from './DreamWorld';
import { DreamMessenger } from './DreamMessenger';
import { DreamStarMap } from './DreamStarMap';
import { DreamSquare } from './DreamSquare';

type SubTab = 'analyze' | 'world' | 'messenger' | 'starmap' | 'square' | 'journal' | 'encyclopedia';

const SUB_TABS: { id: SubTab; label: string; emoji: string }[] = [
  { id: 'analyze', label: '梦境解析', emoji: '🔮' },
  { id: 'world', label: '3D 世界', emoji: '🌍' },
  { id: 'messenger', label: '信使游戏', emoji: '📨' },
  { id: 'starmap', label: '梦境星图', emoji: '✨' },
  { id: 'square', label: '梦境广场', emoji: '🌐' },
  { id: 'journal', label: '梦境日记', emoji: '📓' },
  { id: 'encyclopedia', label: '符号百科', emoji: '📚' },
];
export function DreamSpace() {
  const [subTab, setSubTab] = useState<SubTab>('analyze');
  const [dreamText, setDreamText] = useState('');
  const [useAI, setUseAI] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DreamRecord | null>(null);
  const [journalKey, setJournalKey] = useState(0);

  const handleAnalyze = async () => {
    if (!dreamText.trim()) return;
    setIsAnalyzing(true);
    try {
      const data = await analyzeDream(dreamText, useAI);
      setResult(data);
      setJournalKey(k => k + 1);
    } catch {
      alert('梦境解析失败，请稍后重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setDreamText('');
    setResult(null);
  };

  const handleLoadDream = (record: DreamRecord) => {
    setResult(record);
    setDreamText(record.dream_text);
    setSubTab('analyze');
  };

  return (
    <div className="settings-panel" style={{ overflowY: 'auto' }}>
      <h2 className="pixel-title">🌙 梦境空间</h2>

      {/* 子标签 */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
        {SUB_TABS.map(t => (
          <PixelButton
            key={t.id}
            variant="nav"
            active={subTab === t.id}
            onClick={() => setSubTab(t.id)}
            style={{ fontSize: 10, padding: '6px 12px', minWidth: 0 }}
          >
            {t.emoji} {t.label}
          </PixelButton>
        ))}
      </div>

      {/* ── 梦境解析 ──────────────────────────── */}
      {subTab === 'analyze' && (
        <>
          <div className="settings-group glass-effect" style={{ marginBottom: 20 }}>
            <h3 className="pixel-subtitle">记录你的梦境</h3>
            <textarea
              value={dreamText}
              onChange={(e) => setDreamText(e.target.value)}
              placeholder="请尽可能详细地描述你的梦境...&#10;&#10;例如：我梦见自己在飞翔，周围是蓝天白云，感觉非常自由..."
              style={{
                width: '100%', minHeight: 130, padding: 12,
                background: 'rgba(7, 8, 17, 0.5)', border: '3px solid #2a3b5a',
                color: '#e0e0e0', fontFamily: "'Press Start 2P', 'Zpix', monospace",
                fontSize: 12, resize: 'vertical', outline: 'none',
              }}
            />
            <div style={{ marginTop: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
              <label style={{ fontSize: 12, color: '#9ca3af' }}>
                <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} style={{ marginRight: 6 }} />
                使用 AI 增强分析
              </label>
            </div>
            <div style={{ marginTop: 14, display: 'flex', gap: 10 }}>
              <PixelButton variant="primary" onClick={handleAnalyze} disabled={isAnalyzing || !dreamText.trim()} style={{ flex: 1 }}>
                {isAnalyzing ? '🔮 解析中...' : '✨ 解析梦境'}
              </PixelButton>
              <PixelButton variant="secondary" onClick={handleClear} disabled={!dreamText && !result}>
                🗑️ 清空
              </PixelButton>
            </div>
          </div>

          {result && (
            <>
              <DreamCard
                dreamText={result.dream_text}
                symbols={result.detected_symbols}
                dreamDate={result.dream_date}
              />
              <div className="settings-group glass-effect">
                <h3 className="pixel-subtitle">🔮 梦境解析结果</h3>
                <div style={{ fontSize: 10, color: '#888', marginBottom: 8 }}>
                  {new Date(result.dream_date).toLocaleDateString('zh-CN')} · {result.analysis_type === 'ai_enhanced' ? '🤖 AI 增强' : '📖 传统解梦'}
                </div>
                {result.detected_symbols.length > 0 && (
                  <div style={{ marginBottom: 14 }}>
                    <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 8 }}>
                      检测到 {result.detected_symbols.length} 个梦境符号：
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {result.detected_symbols.map((item, idx) => (
                        <span key={idx} style={{ background: 'rgba(58, 123, 213, 0.2)', border: '2px solid #4a77c5', padding: '4px 8px', fontSize: 10 }}>
                          {item.emoji} {item.symbol}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div style={{ background: 'rgba(7, 8, 17, 0.3)', border: '2px solid #2a3b5a', padding: 16, whiteSpace: 'pre-wrap', lineHeight: 1.8, fontSize: 12 }}>
                  {result.ai_analysis || result.traditional_analysis || '暂无解析内容'}
                </div>
              </div>
            </>
          )}
          {!result && !isAnalyzing && (
            <div className="empty-state">
              <div className="empty-state__icon">🌌</div>
              <div className="empty-state__text">在上方输入你的梦境，点击"解析梦境"开始探索潜意识的秘密</div>
            </div>
          )}
        </>
      )}

      {/* ── 3D 梦境世界 ──────────────────────── */}
      {subTab === 'world' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">🌍 梦境世界</h3>
          <p style={{ fontSize: 10, color: '#888', marginBottom: 10 }}>
            你的梦境化作一颗微型星球。拖拽旋转探索，点击符号查看解读
          </p>
          <DreamWorld
            dreamText={result?.dream_text || dreamText}
            symbols={result?.detected_symbols || []}
          />
        </div>
      )}

      {/* ── 梦境信使游戏 ──────────────────────── */}
      {subTab === 'messenger' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">📨 梦境信使</h3>
          <p style={{ fontSize: 10, color: '#888', marginBottom: 10 }}>
            将解梦信件送达梦境的居民们！点击解析中心 NPC 领取任务，再点击对应符号完成送达
          </p>
          <DreamMessenger
            dreamText={result?.dream_text || dreamText}
            symbols={result?.detected_symbols || []}
          />
        </div>
      )}

      {/* ── 梦境星图 ──────────────────────────── */}
      {subTab === 'starmap' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">✨ 梦境星图</h3>
          <p style={{ fontSize: 10, color: '#888', marginBottom: 10 }}>
            每个梦境化作一颗星，相同类型的符号聚成星座。点击星星查看梦境详情
          </p>
          <DreamStarMap />
        </div>
      )}

      {/* ── 梦境广场 ──────────────────────────── */}
      {subTab === 'square' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">🌐 匿名梦境广场</h3>
          <DreamSquare />
        </div>
      )}

      {/* ── 梦境日记 ──────────────────────────── */}
      {subTab === 'journal' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">📓 梦境日记</h3>
          <DreamJournal onLoadDream={handleLoadDream} refreshKey={journalKey} />
        </div>
      )}

      {/* ── 符号百科 ──────────────────────────── */}
      {subTab === 'encyclopedia' && (
        <div className="settings-group glass-effect">
          <h3 className="pixel-subtitle">📚 梦境符号百科</h3>
          <p style={{ fontSize: 10, color: '#888', marginBottom: 14 }}>
            探索梦境中常见符号的象征意义，帮助你更好地理解潜意识的语言
          </p>
          <SymbolEncyclopedia />
        </div>
      )}
    </div>
  );
}

export default DreamSpace;
