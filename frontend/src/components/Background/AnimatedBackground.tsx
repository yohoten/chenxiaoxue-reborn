/**
 * 动态背景组件
 * 支持 GIF 和静态图片背景，保持与原 PyQt 版本一致的美学风格
 */

import { useEffect, useRef, useState } from 'react';
import { getBackgrounds } from '../../services/api';
import type { ResourceFile } from '../../types';

interface AnimatedBackgroundProps {
  interval?: number; // 轮播间隔 (ms)
}

export function AnimatedBackground({
  interval = 30000,
}: AnimatedBackgroundProps) {
  const [backgrounds, setBackgrounds] = useState<ResourceFile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // 加载背景列表
  useEffect(() => {
    getBackgrounds()
      .then((data) => {
        if (data.backgrounds.length > 0) {
          setBackgrounds(data.backgrounds);
          setLoaded(true);
        }
      })
      .catch(() => {
        // 静默失败 - 使用纯色背景
        setLoaded(true);
      });
  }, []);

  // 自动轮播
  useEffect(() => {
    if (backgrounds.length <= 1) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % backgrounds.length);
    }, interval);

    return () => clearInterval(timer);
  }, [backgrounds.length, interval]);

  if (!loaded || backgrounds.length === 0) {
    return (
      <div
        className="background-layer"
        style={{
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        }}
      />
    );
  }

  const current = backgrounds[currentIndex];

  return (
    <div className="background-layer">
      <img
        ref={imgRef}
        src={current.path}
        alt={current.name}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          opacity: 0.75,
          transition: 'opacity 0.5s ease',
        }}
      />
      {/* 半透明遮罩 */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(26, 26, 46, 0.2)',
        }}
      />
    </div>
  );
}
