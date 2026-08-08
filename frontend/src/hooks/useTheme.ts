/**
 * 主题管理器 — class 切换方案，与 CSS :root 变量联动
 */

import { useState, useEffect } from 'react';

export type ThemeType = 'pixel-dark' | 'pixel-light' | 'cyberpunk' | 'minimal';

const themes: Record<ThemeType, { name: string }> = {
  'pixel-dark':  { name: '像素深色' },
  'pixel-light': { name: '像素浅色' },
  'cyberpunk':   { name: '赛博朋克' },
  'minimal':     { name: '极简' },
};

export const useTheme = () => {
  const [currentTheme, setCurrentTheme] = useState<ThemeType>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as ThemeType) || 'pixel-dark';
  });

  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    // 移除所有旧主题 class
    (Object.keys(themes) as ThemeType[]).forEach(t =>
      document.documentElement.classList.remove(`theme-${t}`)
    );
    // 添加当前主题 class
    document.documentElement.classList.add(`theme-${currentTheme}`);
    localStorage.setItem('theme', currentTheme);

    setIsTransitioning(true);
    setTimeout(() => setIsTransitioning(false), 300);
  }, [currentTheme]);

  const toggleTheme = (theme: ThemeType) => {
    if (theme === currentTheme) return;
    setCurrentTheme(theme);
  };

  const getAvailableThemes = () =>
    Object.entries(themes).map(([id, config]) => ({
      id: id as ThemeType,
      name: config.name,
    }));

  return { currentTheme, toggleTheme, getAvailableThemes, isTransitioning };
};
