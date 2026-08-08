/**
 * 匿名梦境广场 — 浏览他人的梦境摘要
 */
import { useState, useEffect } from 'react';

interface SquareDream {
  id: number; dream_snippet: string; symbols: string[];
  emotion: string; date: string; analysis_type: string;
}

export function DreamSquare() {
  const [dreams, setDreams] = useState<SquareDream[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    import('../../services/api').then(({ getDreamSquare }) => {
      getDreamSquare()
        .then(d => { if (d?.items) setDreams(d.items); })
        .catch(() => {})
        .finally(() => setLoading(false));
    });
  }, []);

  const emotionEmoji: Record<string, string> = {
    happy: '😊', sad: '😢', neutral: '😐', anxious: '😰', excited: '🤩', curious: '🤔',
  };

  if (loading) return <div style={{ padding: 30, textAlign: 'center', color: '#888', fontSize: 11 }}>加载梦境广场...</div>;

  return (
    <div>
      <p style={{ fontSize: 10, color: '#888', marginBottom: 14, textAlign: 'center' }}>
        🌐 匿名梦境广场 · {dreams.length} 个梦境在漂流
      </p>

      {dreams.length === 0 ? (
        <p style={{ color: '#888', fontSize: 11, textAlign: 'center', padding: 30 }}>还没有公开的梦境</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 10 }}>
          {dreams.map(dream => (
            <div key={dream.id} style={{
              background: 'rgba(7,8,17,0.4)', border: '2px solid #2a3b5a',
              padding: 12, display: 'flex', flexDirection: 'column',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 14 }}>{emotionEmoji[dream.emotion] || '😐'}</span>
                <span style={{ fontSize: 8, color: '#666' }}>{dream.date}</span>
              </div>
              <p style={{ fontSize: 10, lineHeight: 1.6, color: '#ccc', flex: 1, margin: 0 }}>
                {dream.dream_snippet}
              </p>
              {dream.symbols.length > 0 && (
                <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap', marginTop: 8 }}>
                  {dream.symbols.map((s, i) => (
                    <span key={i} style={{
                      background: 'rgba(58,123,213,0.15)', border: '1px solid #2a3b5a',
                      padding: '1px 5px', fontSize: 8, color: '#9ca3af',
                    }}>
                      {s}
                    </span>
                  ))}
                </div>
              )}
              <span style={{ fontSize: 7, color: '#555', marginTop: 6 }}>
                {dream.analysis_type === 'ai_enhanced' ? '🤖 AI' : '📖 传统'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DreamSquare;
