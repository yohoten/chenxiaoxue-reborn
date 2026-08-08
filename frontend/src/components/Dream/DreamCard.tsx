/**
 * 梦境卡片组件
 * 像素风梦境分享卡片，可保存和展示
 */
import { useState, useEffect } from 'react';
import { generateDreamCard, recommendSoundscape } from '../../services/api';

interface DreamCardData {
  title: string;
  mood: string;
  mood_emoji: string;
  poetic_line: string;
  symbols_summary: string;
  suggested_music: string;
  color_theme: string;
}

interface SoundscapeData {
  music_type: string;
  description: string;
  color_palette: string[];
  bpm_range: string;
}

interface Props {
  dreamText: string;
  symbols: Array<{ symbol: string }>;
  dreamDate?: string;
}

export function DreamCard({ dreamText, symbols, dreamDate }: Props) {
  const [card, setCard] = useState<DreamCardData | null>(null);
  const [soundscape, setSoundscape] = useState<SoundscapeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showSoundscape, setShowSoundscape] = useState(false);

  useEffect(() => {
    loadCard();
  }, [dreamText]);

  async function loadCard() {
    setLoading(true);
    try {
      const [cardData, soundData] = await Promise.all([
        generateDreamCard(dreamText, symbols.map(s => ({ symbol: s.symbol }))),
        recommendSoundscape(symbols.map(s => s.symbol)),
      ]);
      setCard(cardData);
      setSoundscape(soundData);
    } catch {
      // 降级：本地生成
      setCard({
        title: '🌙 梦境卡片',
        mood: 'neutral',
        mood_emoji: '🌙',
        poetic_line: '每个梦，都是潜意识的低语',
        symbols_summary: symbols.map(s => s.symbol).join('、') || '梦中的秘密',
        suggested_music: 'lofi-chill',
        color_theme: '#4a6a5a',
      });
    }
    setLoading(false);
  }

  if (loading) {
    return <div style={{ padding: 20, textAlign: 'center', color: '#888', fontSize: 11 }}>生成卡片中...</div>;
  }

  if (!card) return null;

  return (
    <div>
      {/* 梦境卡片 */}
      <div style={{
        background: `linear-gradient(135deg, ${card.color_theme}22, ${card.color_theme}08)`,
        border: `3px solid ${card.color_theme}`,
        padding: 20,
        position: 'relative',
        overflow: 'hidden',
        marginBottom: 16,
      }}>
        {/* 像素装饰边框 */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 3,
          background: `repeating-linear-gradient(90deg, ${card.color_theme}, ${card.color_theme} 8px, transparent 8px, transparent 16px)`,
        }} />
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 3,
          background: `repeating-linear-gradient(90deg, ${card.color_theme}, ${card.color_theme} 8px, transparent 8px, transparent 16px)`,
        }} />

        {/* 标题 */}
        <div style={{ textAlign: 'center', marginBottom: 12 }}>
          <div style={{ fontSize: 32, marginBottom: 4 }}>{card.mood_emoji}</div>
          <h3 style={{ fontSize: 13, margin: 0, color: card.color_theme }}>{card.title}</h3>
          {dreamDate && (
            <p style={{ fontSize: 9, color: '#666', marginTop: 4 }}>
              {new Date(dreamDate).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          )}
        </div>

        {/* 诗意行 */}
        <div style={{
          textAlign: 'center', padding: '12px 0', borderTop: `1px dashed ${card.color_theme}44`,
          borderBottom: `1px dashed ${card.color_theme}44`, marginBottom: 12,
        }}>
          <p style={{ fontSize: 11, fontStyle: 'italic', color: '#ccc', margin: 0, lineHeight: 1.8 }}>
            "{card.poetic_line}"
          </p>
        </div>

        {/* 符号摘要 */}
        <p style={{ fontSize: 10, color: '#999', textAlign: 'center', marginBottom: 12, lineHeight: 1.6 }}>
          {card.symbols_summary}
        </p>

        {/* 音景推荐 */}
        <div style={{ textAlign: 'center' }}>
          <button
            className="pixel-btn"
            onClick={() => setShowSoundscape(!showSoundscape)}
            style={{ fontSize: 9, padding: '4px 12px', minWidth: 0 }}
          >
            🎵 {showSoundscape ? '收起音景' : '推荐音景'}
          </button>
        </div>
      </div>

      {/* 音景详情 */}
      {showSoundscape && soundscape && (
        <div style={{
          background: 'rgba(7,8,17,0.5)', border: '2px solid #2a3b5a',
          padding: 16, marginBottom: 16,
        }}>
          <h4 style={{ fontSize: 11, marginBottom: 10, color: '#9ca3af' }}>🎵 推荐梦境音景</h4>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 10 }}>
            <div style={{ flex: 1, minWidth: 120 }}>
              <div style={{ fontSize: 9, color: '#666' }}>音乐类型</div>
              <div style={{ fontSize: 12, color: '#3a7bd5', fontFamily: "'Press Start 2P', monospace" }}>
                {soundscape.music_type}
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 80 }}>
              <div style={{ fontSize: 9, color: '#666' }}>节奏</div>
              <div style={{ fontSize: 12, color: '#ccc' }}>{soundscape.bpm_range}</div>
            </div>
          </div>
          <p style={{ fontSize: 10, color: '#999', lineHeight: 1.6, marginBottom: 10 }}>
            {soundscape.description}
          </p>
          <div style={{ display: 'flex', gap: 6 }}>
            {soundscape.color_palette.map((color, i) => (
              <div key={i} style={{
                width: 24, height: 24, background: color,
                border: '2px solid #333',
              }} title={color} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DreamCard;
