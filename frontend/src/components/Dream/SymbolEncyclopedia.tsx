/**
 * 梦境符号百科
 * 可浏览的梦境符号图鉴
 */
import { useState, useEffect } from 'react';
import { getSymbolEncyclopedia } from '../../services/api';
import type { SymbolEncyclopediaItem } from '../../types';

export function SymbolEncyclopedia() {
  const [symbols, setSymbols] = useState<SymbolEncyclopediaItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('');
  const [selectedSymbol, setSelectedSymbol] = useState<SymbolEncyclopediaItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSymbols();
  }, []);

  async function loadSymbols(cat?: string) {
    setLoading(true);
    try {
      const data = await getSymbolEncyclopedia(cat || undefined);
      setSymbols(data.symbols);
      if (!cat) setCategories(data.categories);
    } catch { /* ignore */ }
    setLoading(false);
  }

  return (
    <div>
      {/* 分类筛选 */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
        <button
          className={`pixel-btn ${!activeCategory ? 'pixel-btn--active' : ''}`}
          onClick={() => { setActiveCategory(''); loadSymbols(); }}
          style={{ fontSize: 10, padding: '4px 10px', minWidth: 0 }}
        >
          全部 ({symbols.length})
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            className={`pixel-btn ${activeCategory === cat ? 'pixel-btn--active' : ''}`}
            onClick={() => { setActiveCategory(cat); loadSymbols(cat); }}
            style={{ fontSize: 10, padding: '4px 10px', minWidth: 0 }}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <p style={{ color: '#888', fontSize: 12, textAlign: 'center', padding: 40 }}>加载中...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: 8 }}>
          {symbols.map(item => (
            <button
              key={item.symbol}
              onClick={() => setSelectedSymbol(item)}
              style={{
                background: 'rgba(7, 8, 17, 0.5)',
                border: '2px solid #2a3b5a',
                padding: '10px 8px',
                cursor: 'pointer',
                textAlign: 'center',
                color: '#e0e0e0',
                fontFamily: "'Press Start 2P', monospace",
                fontSize: 9,
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 4 }}>{item.emoji}</div>
              <div>{item.symbol}</div>
            </button>
          ))}
        </div>
      )}

      {/* 详情弹窗 */}
      {selectedSymbol && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
        }} onClick={() => setSelectedSymbol(null)}>
          <div style={{
            background: '#1a1a2e', border: '3px solid #4a77c5',
            padding: 24, maxWidth: 450, width: '90%', maxHeight: '80vh', overflowY: 'auto',
          }} onClick={e => e.stopPropagation()}>
            <div style={{ fontSize: 40, textAlign: 'center', marginBottom: 8 }}>
              {selectedSymbol.emoji}
            </div>
            <h3 style={{ textAlign: 'center', marginBottom: 4, fontSize: 14 }}>
              {selectedSymbol.symbol}
            </h3>
            <p style={{ textAlign: 'center', fontStyle: 'italic', color: '#888', fontSize: 10, marginBottom: 16 }}>
              {selectedSymbol.category}
            </p>

            <h4 style={{ fontSize: 11, color: '#9ca3af', marginBottom: 8 }}>解读</h4>
            {selectedSymbol.interpretations.map((interp, i) => (
              <p key={i} style={{
                fontSize: 11, lineHeight: 1.7, marginBottom: 6,
                padding: '6px 10px', background: 'rgba(58,123,213,0.1)', border: '1px solid #2a3b5a',
              }}>
                {interp}
              </p>
            ))}

            {selectedSymbol.related_symbols.length > 0 && (
              <>
                <h4 style={{ fontSize: 11, color: '#9ca3af', marginTop: 12, marginBottom: 6 }}>相关符号</h4>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {selectedSymbol.related_symbols.map(rs => (
                    <span key={rs} style={{
                      background: 'rgba(58,123,213,0.2)', border: '1px solid #4a77c5',
                      padding: '2px 8px', fontSize: 10,
                    }}>{rs}</span>
                  ))}
                </div>
              </>
            )}

            <button
              className="pixel-btn"
              onClick={() => setSelectedSymbol(null)}
              style={{ width: '100%', marginTop: 16, fontSize: 11 }}
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SymbolEncyclopedia;
