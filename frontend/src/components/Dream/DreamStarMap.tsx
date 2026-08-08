/**
 * 梦境星图 — 每个梦境化作一颗星星，构成个人星空
 */
import { useEffect, useRef, useState } from 'react';

interface Star {
  id: number; dream_text: string; symbols: string[];
  emoji: string; mood: string; x: number; y: number;
  brightness: number; date: string;
}

interface Constellation {
  name: string; stars: Array<{ id: number; symbol: string }>; count: number;
}

interface StarMapData {
  stars: Star[]; total: number; constellations: Constellation[];
}

interface Props {
  onSelectDream?: (id: number) => void;
}

export function DreamStarMap({ onSelectDream }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<StarMapData | null>(null);
  const [selectedStar, setSelectedStar] = useState<Star | null>(null);
  const [hoveredStar, setHoveredStar] = useState<Star | null>(null);
  const [loading, setLoading] = useState(true);
  const starMap = useRef<Map<string, Star>>(new Map());

  useEffect(() => {
    import('../../services/api').then(({ getDreamStarMap }) => {
      getDreamStarMap()
        .then(d => { setData(d); setLoading(false); })
        .catch(() => setLoading(false));
    });
  }, []);

  // Canvas 渲染
  useEffect(() => {
    if (!data || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width = canvas.offsetWidth * 2;
    const h = canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);
    const cw = canvas.offsetWidth;
    const ch = canvas.offsetHeight;

    // 深空背景
    const bgGrad = ctx.createRadialGradient(cw / 2, ch / 2, 0, cw / 2, ch / 2, cw);
    bgGrad.addColorStop(0, '#1a1a3e');
    bgGrad.addColorStop(1, '#0a0a1a');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, cw, ch);

    // 背景散星
    for (let i = 0; i < 100; i++) {
      const sx = Math.random() * cw;
      const sy = Math.random() * ch;
      ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.3 + 0.1})`;
      ctx.beginPath();
      ctx.arc(sx, sy, Math.random() * 1.2, 0, Math.PI * 2);
      ctx.fill();
    }

    // 星座连线
    data.constellations.forEach((constellation, ci) => {
      if (constellation.count < 2) return;
      const color = `hsl(${ci * 60}, 50%, 60%)`;
      ctx.strokeStyle = color.replace('60%)', '60%, 0.2)');
      ctx.lineWidth = 0.5;

      const starsInConst = constellation.stars
        .map(cs => data.stars.find(s => s.id === cs.id))
        .filter(Boolean) as Star[];

      for (let i = 0; i < starsInConst.length - 1; i++) {
        for (let j = i + 1; j < starsInConst.length; j++) {
          const sx = starsInConst[i].x * 80 + cw / 2;
          const sy = starsInConst[i].y * 80 + ch / 2;
          const ex = starsInConst[j].x * 80 + cw / 2;
          const ey = starsInConst[j].y * 80 + ch / 2;
          const dist = Math.hypot(ex - sx, ey - sy);
          if (dist < 200) {
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(ex, ey);
            ctx.stroke();
          }
        }
      }
    });

    // 梦境星星
    const m = starMap.current;
    m.clear();
    data.stars.forEach(star => {
      const sx = star.x * 80 + cw / 2;
      const sy = star.y * 80 + ch / 2;
      const r = 3 + star.brightness * 5;

      // 光晕
      const glow = ctx.createRadialGradient(sx, sy, 0, sx, sy, r * 2);
      const moodColors: Record<string, string> = {
        happy: '255,220,100', sad: '100,140,220', neutral: '180,200,220',
        anxious: '220,140,100', excited: '255,180,60', curious: '100,220,180',
      };
      const mc = moodColors[star.mood] || moodColors.neutral;
      glow.addColorStop(0, `rgba(${mc},${star.brightness})`);
      glow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(sx, sy, r * 2, 0, Math.PI * 2);
      ctx.fill();

      // 星星主体
      ctx.fillStyle = `rgba(${mc},1)`;
      ctx.beginPath();
      ctx.arc(sx, sy, r, 0, Math.PI * 2);
      ctx.fill();

      m.set(`${sx},${sy}`, star);
    });

    // 中心标签
    ctx.fillStyle = '#888';
    ctx.font = '10px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText(`${data.total} 个梦境`, cw / 2, ch - 20);

    // 点击处理
    const onClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      for (const [key, star] of m) {
        const [sx, sy] = key.split(',').map(Number);
        if (Math.hypot(mx - sx, my - sy) < 12) {
          setSelectedStar(star);
          return;
        }
      }
      setSelectedStar(null);
    };

    const onMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      let found: Star | null = null;
      for (const [key, star] of m) {
        const [sx, sy] = key.split(',').map(Number);
        if (Math.hypot(mx - sx, my - sy) < 12) { found = star; break; }
      }
      setHoveredStar(found);
      canvas.style.cursor = found ? 'pointer' : 'default';
    };

    canvas.addEventListener('click', onClick);
    canvas.addEventListener('mousemove', onMove);

    return () => {
      canvas.removeEventListener('click', onClick);
      canvas.removeEventListener('mousemove', onMove);
    };
  }, [data]);

  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#888' }}>加载星图...</div>;
  if (!data || data.total === 0) {
    return <div style={{ padding: 40, textAlign: 'center', color: '#888', fontSize: 11 }}>还没有梦境记录，去解析你的第一个梦吧 🌙</div>;
  }

  return (
    <div style={{ position: 'relative' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: 380, borderRadius: 8, background: '#0a0a1a' }} />

      {/* 悬停提示 */}
      {hoveredStar && (
        <div style={{
          position: 'absolute', top: 8, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(10,10,30,0.9)', border: '1px solid #444',
          padding: '6px 12px', fontSize: 10, color: '#ccc', whiteSpace: 'nowrap',
          pointerEvents: 'none', zIndex: 10,
        }}>
          {hoveredStar.emoji} {hoveredStar.dream_text} · {hoveredStar.date}
        </div>
      )}

      {/* 选中星星详情 */}
      {selectedStar && (
        <div style={{
          position: 'absolute', bottom: 8, left: 8, right: 8,
          background: 'rgba(10,10,30,0.95)', border: '2px solid #4a77c5',
          padding: 12, zIndex: 10,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 16 }}>{selectedStar.emoji}</span>
              <span style={{ fontSize: 11, color: '#ccc', marginLeft: 8 }}>{selectedStar.mood}</span>
              <span style={{ fontSize: 9, color: '#888', marginLeft: 8 }}>{selectedStar.date}</span>
            </div>
            <button onClick={() => setSelectedStar(null)} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: 14 }}>×</button>
          </div>
          <p style={{ fontSize: 10, color: '#999', marginTop: 6, lineHeight: 1.5 }}>{selectedStar.dream_text}</p>
          {selectedStar.symbols.length > 0 && (
            <div style={{ display: 'flex', gap: 4, marginTop: 6 }}>
              {selectedStar.symbols.map((s, i) => (
                <span key={i} style={{ background: 'rgba(58,123,213,0.2)', border: '1px solid #2a3b5a', padding: '1px 6px', fontSize: 9 }}>{s}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 星座图例 */}
      <div style={{
        position: 'absolute', top: 8, right: 8,
        background: 'rgba(0,0,0,0.5)', padding: '4px 8px', fontSize: 9, color: '#888',
        borderRadius: 4, pointerEvents: 'none',
      }}>
        {data.constellations.slice(0, 5).map(c => (
          <div key={c.name}>{c.name}: {c.count}星</div>
        ))}
      </div>
    </div>
  );
}

export default DreamStarMap;
