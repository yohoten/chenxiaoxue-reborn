/**
 * 情感指示器组件
 * 整合角色面板和状态显示
 */

import React from 'react';
import { CharacterPanel } from './CharacterPanel';

interface EmotionIndicatorProps {
  emotion: string;
  glassEffect?: boolean;
}

const EMOTION_MAP: Record<string, { emoji: string; label: string }> =
  {
    ecstatic: { emoji: '😊✨🎉', label: '狂喜' },
    happy: { emoji: '😊', label: '开心' },
    content: { emoji: '🙂', label: '满足' },
    neutral: { emoji: '😐', label: '平静' },
    confused: { emoji: '😕', label: '困惑' },
    sad: { emoji: '😢', label: '难过' },
    angry: { emoji: '😠', label: '生气' },
    embarrassed: { emoji: '😳', label: '尴尬' },
    surprised: { emoji: '😲', label: '惊讶' },
  };

export function EmotionIndicator({
  emotion,
  glassEffect = false,
}: EmotionIndicatorProps) {
  const info = EMOTION_MAP[emotion] || {
    emoji: '😐',
    label: '平静',
  };

  return (
    <div className="left-panel-section">
      {/* 角色面板 */}
      <CharacterPanel emotion={emotion} glassEffect={glassEffect} />

      {/* 情感状态文本 */}
      <div className={`status-panel__emotion ${glassEffect ? 'glass-effect' : ''}`}>
        心情: {info.label} {info.emoji}
      </div>
    </div>
  );
}
