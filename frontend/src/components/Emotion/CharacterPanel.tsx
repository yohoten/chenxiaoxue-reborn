/**
 * 角色面板 — 精简情感标签
 */

import { useState } from 'react';

interface CharacterPanelProps {
  emotion?: string;
  glassEffect?: boolean;
}

const CHARACTER_IMAGE = '/assets/characters/20200922232838_082dc.gif';

const EMOTION_LABEL: Record<string, string> = {
  neutral: '静', happy: '悦', sad: '悲', angry: '怒',
  surprised: '惊', confused: '惑', ecstatic: '狂', content: '安',
  embarrassed: '羞',
};

export function CharacterPanel({ emotion = 'neutral', glassEffect = false }: CharacterPanelProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const label = EMOTION_LABEL[emotion] || '静';

  return (
    <div className={`character-panel ${glassEffect ? 'glass-effect' : ''}`}>
      <div style={{
        position: 'relative', width: '100%', height: '100%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        overflow: 'hidden',
      }}>
        <img
          src={CHARACTER_IMAGE}
          alt="Character"
          onLoad={() => setImageLoaded(true)}
          style={{
            maxWidth: '100%', maxHeight: '100%', objectFit: 'contain',
            opacity: imageLoaded ? 1 : 0,
            transition: 'opacity 0.4s ease',
          }}
        />

        <div style={{
          position: 'absolute', bottom: 10, left: '50%',
          transform: 'translateX(-50%)',
          fontSize: 13, fontWeight: 'bold',
          background: 'rgba(26, 26, 46, 0.75)',
          color: 'var(--text-primary)',
          padding: '3px 10px',
          fontFamily: 'var(--font-ui)',
        }}>
          {label}
        </div>
      </div>
    </div>
  );
}
