/**
 * 像素小人动画组件 - 3帧循环行走/站立动画
 */
import React, { useState, useEffect } from 'react';

interface PixelCharacterProps {
  action?: 'idle' | 'walking' | 'thinking';
  size?: number;
}

export const PixelCharacter: React.FC<PixelCharacterProps> = ({
  action = 'idle',
  size = 32,
}) => {
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % 3);
    }, 300);

    return () => clearInterval(interval);
  }, []);

  // 简单的像素小人SVG（3帧）
  const frames = {
    idle: [
      // 站立帧1
      <svg key="0" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
      </svg>,
      // 站立帧2（轻微晃动）
      <svg key="1" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="4" y="7" width="1" height="2" fill="#ff9d00" />
      </svg>,
      // 站立帧3
      <svg key="2" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="11" y="7" width="1" height="2" fill="#ff9d00" />
      </svg>,
    ],
    walking: [
      // 走路帧1
      <svg key="0" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="4" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="10" y="11" width="2" height="3" fill="#2d4a6f" />
      </svg>,
      // 走路帧2
      <svg key="1" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
      </svg>,
      // 走路帧3
      <svg key="2" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="6" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="8" y="11" width="2" height="3" fill="#2d4a6f" />
      </svg>,
    ],
    thinking: [
      // 思考帧1
      <svg key="0" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
        <circle cx="13" cy="3" r="1" fill="#fff" opacity="0.8" />
      </svg>,
      // 思考帧2
      <svg key="1" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
        <circle cx="13" cy="3" r="1.5" fill="#fff" opacity="0.6" />
      </svg>,
      // 思考帧3
      <svg key="2" width={size} height={size} viewBox="0 0 16 16">
        <rect x="6" y="2" width="4" height="4" fill="#ff9d00" />
        <rect x="5" y="6" width="6" height="5" fill="#4a77c5" />
        <rect x="5" y="11" width="2" height="3" fill="#2d4a6f" />
        <rect x="9" y="11" width="2" height="3" fill="#2d4a6f" />
        <circle cx="13" cy="3" r="2" fill="#fff" opacity="0.4" />
      </svg>,
    ],
  };

  return (
    <div style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      {frames[action][frame]}
    </div>
  );
};

/**
 * 加载动画 - 像素风格检索中
 */
export const PixelLoading: React.FC<{ text?: string }> = ({ text = '检索档案中' }) => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-indicator" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <PixelCharacter action="thinking" size={24} />
      <span>{text}{dots}</span>
    </div>
  );
};