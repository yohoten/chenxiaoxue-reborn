/**
 * ECG 心电状态栏 — 增强版
 * - CSS 模式：真实 P-Q-R-S-T 波形，BPM 驱动速度
 * - Canvas 模式：剧烈情绪动态渲染，后台自动暂停
 * - QRS 辉光脉冲 + 心率过渡动画
 */

import React from 'react';
import { useEffect, useRef, useState, useMemo, useCallback } from 'react';

interface ECGStatusBarProps {
  isActive?: boolean;
  emotion?: string | null;
  glassEffect?: boolean;
}

// 情感 → (心率, 颜色, 强度)
const EMOTION_CONFIG: Record<string, { heartRate: number; color: string; intensity: number }> = {
  neutral:   { heartRate: 70,  color: '#4ade80', intensity: 1.0 },
  happy:     { heartRate: 85,  color: '#ff9d00', intensity: 1.2 },
  joy:       { heartRate: 90,  color: '#ffcc00', intensity: 1.3 },
  excited:   { heartRate: 100, color: '#ff6b6b', intensity: 1.5 },
  surprised: { heartRate: 95,  color: '#ffd43b', intensity: 1.4 },
  sad:       { heartRate: 60,  color: '#4a77c5', intensity: 0.8 },
  angry:     { heartRate: 110, color: '#ff4500', intensity: 1.6 },
  fear:      { heartRate: 105, color: '#ff6347', intensity: 1.5 },
  disgust:   { heartRate: 75,  color: '#8b4513', intensity: 0.9 },
  thinking:  { heartRate: 72,  color: '#4ecdc4', intensity: 1.0 },
  default:   { heartRate: 70,  color: '#4ade80', intensity: 1.0 },
};

const INTENSE_EMOTIONS = new Set(['excited', 'angry', 'fear', 'surprised']);

// 生成真实 ECG P-Q-R-S-T 波形路径（一个心动周期 100 单位宽）
function makeBeatPath(offsetX: number, baseY = 40): string {
  const x = (v: number) => (offsetX + v).toFixed(1);
  return [
    `M ${x(0)} ${baseY}`,
    `L ${x(4)} ${baseY}`,
    `C ${x(6)} ${baseY - 2}, ${x(8)} ${baseY - 5}, ${x(10)} ${baseY}`,
    `L ${x(18)} ${baseY}`,
    `L ${x(19.5)} ${baseY + 2}`,
    `L ${x(20.5)} ${baseY - 20}`,
    `L ${x(21.5)} ${baseY + 4}`,
    `L ${x(24)} ${baseY}`,
    `C ${x(28)} ${baseY - 1}, ${x(32)} ${baseY}, ${x(34)} ${baseY}`,
    `C ${x(36)} ${baseY - 4}, ${x(40)} ${baseY - 7}, ${x(44)} ${baseY}`,
    `L ${x(100)} ${baseY}`,
  ].join(' ');
}

// 生成连续 N 个心跳周期的 SVG path
function makeECGPath(numBeats: number, width: number, baseY = 40): string {
  const beatWidth = width / numBeats;
  return Array.from({ length: numBeats }, (_, i) =>
    makeBeatPath(i * beatWidth, baseY),
  ).join(' ');
}

const BEATS_PER_VIEW = 3;
const SVG_WIDTH = 900; // 3 beats × 300 each
const BASELINE = 40;

const ECG_PATH_LEFT = makeECGPath(BEATS_PER_VIEW, SVG_WIDTH / 2, BASELINE);
const ECG_PATH_RIGHT = makeECGPath(BEATS_PER_VIEW, SVG_WIDTH / 2, BASELINE);

// 辉光线（半透明宽线，仅 R 尖峰处可见）
function makeGlowPath(numBeats: number, width: number, baseY = 40): string {
  const beatWidth = width / numBeats;
  return Array.from({ length: numBeats }, (_, i) => {
    const ox = i * beatWidth;
    return `M ${(ox + 19.5).toFixed(1)} ${baseY + 2} L ${(ox + 21.5).toFixed(1)} ${baseY}`;
  }).join(' ');
}

const GLOW_PATH_HALF = makeGlowPath(BEATS_PER_VIEW, SVG_WIDTH / 2, BASELINE);

export function ECGStatusBar({ isActive = true, emotion = null, glassEffect = false }: ECGStatusBarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gridCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const [currentHeartRate, setCurrentHeartRate] = useState(70);
  const [currentColor, setCurrentColor] = useState('#4ade80');
  const [currentIntensity, setCurrentIntensity] = useState(1.0);
  const [displayedBPM, setDisplayedBPM] = useState(70);

  const needDynamicRender = useMemo(() => {
    if (!emotion) return false;
    return INTENSE_EMOTIONS.has(emotion.toLowerCase());
  }, [emotion]);

  // 心率平滑过渡
  useEffect(() => {
    if (!emotion) {
      setCurrentHeartRate(70);
      setDisplayedBPM(70);
      setCurrentColor('#4ade80');
      setCurrentIntensity(1.0);
      return;
    }
    const config = EMOTION_CONFIG[emotion.toLowerCase()] || EMOTION_CONFIG.default;
    setCurrentColor(config.color);
    setCurrentIntensity(config.intensity);

    const target = config.heartRate;
    const start = displayedBPM;
    const steps = 30;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      const eased = start + (target - start) * (step / steps);
      setDisplayedBPM(Math.round(eased));
      if (step >= steps) {
        setDisplayedBPM(target);
        setCurrentHeartRate(target);
        clearInterval(timer);
      }
    }, 50);
    return () => clearInterval(timer);
  }, [emotion]);

  // 预渲染网格到离屏 Canvas
  const renderGrid = useCallback((canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.strokeStyle = 'rgba(58, 255, 94, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 20) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 20) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
    ctx.strokeStyle = 'rgba(58, 255, 94, 0.08)';
    ctx.beginPath(); ctx.moveTo(0, canvas.height / 2); ctx.lineTo(canvas.width, canvas.height / 2); ctx.stroke();
  }, []);

  // Canvas 动态渲染（剧烈情绪）
  useEffect(() => {
    if (!needDynamicRender || !isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 预渲染网格
    if (!gridCanvasRef.current) {
      gridCanvasRef.current = document.createElement('canvas');
      gridCanvasRef.current.width = canvas.width;
      gridCanvasRef.current.height = canvas.height;
      renderGrid(gridCanvasRef.current);
    }

    let animationId: number;
    let time = 0;
    let beatTimer = 0;
    const dataPoints: number[] = [];
    const maxDataPoints = 300;

    const generateECGPoint = (t: number, hr: number) => {
      const beatDuration = (60000 / hr);
      const phase = ((t % beatDuration) / beatDuration);
      let value = 0;
      // P wave ~10%
      if (phase >= 0.06 && phase < 0.14) {
        value = Math.sin((phase - 0.06) / 0.08 * Math.PI) * 2.5;
      }
      // QRS complex ~30-36%
      else if (phase >= 0.28 && phase < 0.36) {
        const qrs = (phase - 0.28) / 0.08;
        if (qrs < 0.10) value = -qrs * 20;
        else if (qrs < 0.25) value = Math.sin((qrs - 0.10) / 0.15 * Math.PI) * 30;
        else if (qrs < 0.50) value = -Math.sin((qrs - 0.25) / 0.25 * Math.PI) * 10;
        else value = Math.sin((qrs - 0.50) / 0.50 * Math.PI) * 4;
      }
      // T wave ~55-70%
      else if (phase >= 0.50 && phase < 0.70) {
        value = Math.sin((phase - 0.50) / 0.20 * Math.PI) * 6;
      }
      return value + (Math.random() - 0.5) * 1.2; // 微量噪点
    };

    const draw = () => {
      const w = canvas.width, h = canvas.height;
      const cy = h / 2;
      const hr = currentHeartRate;

      const newVal = generateECGPoint(time, hr);
      dataPoints.push(newVal);
      if (dataPoints.length > maxDataPoints) dataPoints.shift();

      // 检测 R 波峰值 → 辉光计时器
      if (newVal > 20 && beatTimer <= 0) beatTimer = 8;
      if (beatTimer > 0) beatTimer--;

      ctx.clearRect(0, 0, w, h);
      // 离屏网格
      if (gridCanvasRef.current) {
        ctx.drawImage(gridCanvasRef.current, 0, 0);
      }

      const stepX = w / maxDataPoints;
      const glowAlpha = beatTimer > 0 ? 0.3 : 0.06;

      // 辉光层（粗线，半透明）
      if (dataPoints.length > 1) {
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = 6;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.shadowColor = currentColor;
        ctx.shadowBlur = 20;
        ctx.globalAlpha = glowAlpha;
        ctx.beginPath();
        for (let i = 0; i < dataPoints.length; i++) {
          const px = i * stepX, py = cy - dataPoints[i];
          i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
      }

      // 主线
      ctx.strokeStyle = currentColor;
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = currentColor;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      for (let i = 0; i < dataPoints.length; i++) {
        const px = i * stepX, py = cy - dataPoints[i];
        i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // 扫描线
      const scanX = (time / 50) % w;
      const grad = ctx.createLinearGradient(scanX - 30, 0, scanX, 0);
      grad.addColorStop(0, 'rgba(255,255,255,0)');
      grad.addColorStop(1, 'rgba(255,255,255,0.12)');
      ctx.fillStyle = grad;
      ctx.fillRect(scanX - 30, 0, 30, h);

      time += 16;
      if (document.visibilityState !== 'hidden') {
        animationId = requestAnimationFrame(draw);
      } else {
        // 页面隐藏时降低轮询频率
        animationId = window.setTimeout(() => draw(), 500) as unknown as number;
      }
    };

    draw();
    return () => {
      cancelAnimationFrame(animationId);
      clearTimeout(animationId);
    };
  }, [needDynamicRender, isActive, currentHeartRate, currentColor, renderGrid]);

  // BPM → 一个心跳周期的秒数
  const beatDurationSec = currentHeartRate > 0 ? 60 / currentHeartRate : 0.86;
  // CSS 动画滚动速度：一个心跳周期 = beatDurationSec，SVG 宽度包含 3 拍
  const animDuration = beatDurationSec * BEATS_PER_VIEW;

  const emotionLabel = useMemo(() => {
    if (!emotion) return isActive ? '● 系统运行中' : '○ 待机模式';
    const map: Record<string, string> = {
      neutral: '💚 平静', happy: '💛 开心', joy: '✨ 喜悦',
      excited: '❤️ 兴奋', surprised: '😮 惊讶', sad: '💙 忧伤',
      angry: '🔥 激动', fear: '😰 紧张', disgust: '😖 不适',
      thinking: '💭 思考',
    };
    const label = map[emotion.toLowerCase()] || '💚 正常';
    return `${label}  ♥ ${displayedBPM} BPM`;
  }, [emotion, displayedBPM, isActive]);

  return (
    <div className={`ecg-status-bar ${glassEffect ? 'glass-effect' : ''}`}>
      {needDynamicRender ? (
        <canvas
          ref={canvasRef}
          width={300}
          height={80}
          style={{
            width: '100%', height: 80,
            background: 'var(--bg-color)',
            borderRadius: '4px',
            boxShadow: `inset 0 0 20px rgba(0,0,0,0.5), 0 0 12px ${currentColor}20`,
          }}
        />
      ) : (
        <div
          className="ecg-css-container"
          style={{
            width: '100%', height: 80,
            background: 'var(--bg-color)',
            borderRadius: '4px',
            boxShadow: `inset 0 0 20px rgba(0,0,0,0.5), 0 0 8px ${currentColor}18`,
            position: 'relative', overflow: 'hidden',
          }}
        >
          {/* 网格背景（静态 SVG pattern） */}
          <svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0, opacity: 0.05 }}>
            <defs>
              <pattern id="ecg-grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#4ade80" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#ecg-grid)" />
          </svg>

          {/* BPM 驱动速度的滚动 ECG 波形 */}
          <div
            className="ecg-css-line"
            style={{
              position: 'absolute', top: 0, left: 0,
              width: '200%', height: '100%',
              animation: `ecg-css-scroll ${animDuration.toFixed(2)}s linear infinite`,
            }}
          >
            {/* 左半：主体 ECG */}
            <svg
              width="50%" height="100%" style={{ float: 'left' }}
              viewBox={`0 0 ${SVG_WIDTH / 2} 80`}
              preserveAspectRatio="none"
            >
              {/* 辉光线（R 尖峰脉冲） */}
              <path d={GLOW_PATH_HALF} fill="none"
                stroke={currentColor} strokeWidth="10" strokeLinecap="round"
                opacity="0.3"
                style={{ filter: `drop-shadow(0 0 12px ${currentColor})` }}
              />
              {/* 主线 */}
              <path d={ECG_PATH_LEFT} fill="none"
                stroke={currentColor} strokeWidth="2.5"
                strokeLinecap="round" strokeLinejoin="round"
                style={{ filter: `drop-shadow(0 0 5px ${currentColor})` }}
              />
            </svg>
            {/* 右半：无缝循环副本 */}
            <svg
              width="50%" height="100%" style={{ float: 'left' }}
              viewBox={`0 0 ${SVG_WIDTH / 2} 80`}
              preserveAspectRatio="none"
            >
              <path d={GLOW_PATH_HALF} fill="none"
                stroke={currentColor} strokeWidth="10" strokeLinecap="round"
                opacity="0.3"
                style={{ filter: `drop-shadow(0 0 12px ${currentColor})` }}
              />
              <path d={ECG_PATH_RIGHT} fill="none"
                stroke={currentColor} strokeWidth="2.5"
                strokeLinecap="round" strokeLinejoin="round"
                style={{ filter: `drop-shadow(0 0 5px ${currentColor})` }}
              />
            </svg>
          </div>

          {/* QRS 同步脉冲指示灯（右上角） */}
          <div
            style={{
              position: 'absolute', top: 6, right: 10,
              width: 8, height: 8,
              borderRadius: '50%',
              background: currentColor,
              boxShadow: `0 0 8px ${currentColor}, 0 0 16px ${currentColor}`,
              animation: `ecg-beat-pulse ${beatDurationSec.toFixed(2)}s ease-in-out infinite`,
            }}
          />
        </div>
      )}

      {/* BPM 信息栏 — 等宽数字风格 */}
      <div
        style={{
          fontSize: 11, marginTop: 6,
          color: currentColor, textAlign: 'center',
          fontWeight: 'bold',
          fontFamily: '"VT323", "Courier New", monospace',
          letterSpacing: '1px',
          textShadow: `0 0 8px ${currentColor}40`,
        }}
      >
        {emotionLabel}
      </div>
    </div>
  );
}
