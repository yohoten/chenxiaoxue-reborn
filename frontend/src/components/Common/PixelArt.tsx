/**
 * ASCII艺术字生成器 - 像素风格标题
 */

// 简单的像素字体映射表 (5x5点阵)
const PIXEL_FONT: Record<string, string[]> = {
  'A': [
    '  ██  ',
    ' █  █ ',
    '██████',
    '█    █',
    '█    █',
  ],
  'B': [
    '█████ ',
    '█    █',
    '█████ ',
    '█    █',
    '█████ ',
  ],
  'C': [
    ' █████',
    '█     ',
    '█     ',
    '█     ',
    ' █████',
  ],
  // ... 可以继续扩展更多字符
};

/**
 * 将文本转换为ASCII艺术字
 */
export const textToAscii = (text: string): string => {
  const lines: string[] = ['', '', '', '', ''];
  
  for (let i = 0; i < text.length; i++) {
    const char = text[i].toUpperCase();
    const pattern = PIXEL_FONT[char] || ['     ', '     ', '     ', '     ', '     '];
    
    for (let j = 0; j < 5; j++) {
      lines[j] += pattern[j] + ' ';
    }
  }
  
  return lines.join('\n');
};

/**
 * 系统启动动画文本
 */
export const SYSTEM_BOOT_TEXTS = [
  '[系统初始化中...]',
  '[加载情感模块...]',
  '[连接MCP服务器...]',
  '[欢迎进入heademo终端]',
];

/**
 * 打字机效果Hook
 */
import { useState, useEffect } from 'react';

export const useTypewriter = (text: string, speed: number = 50) => {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let index = 0;
    setDisplayText('');
    setIsComplete(false);

    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return { displayText, isComplete };
};

/**
 * 闪烁光标组件
 */
export const BlinkingCursor: React.FC<{ color?: string }> = ({ color = '#ff9d00' }) => {
  return (
    <span
      style={{
        display: 'inline-block',
        width: '8px',
        height: '14px',
        backgroundColor: color,
        animation: 'pixel-blink 1s step-end infinite',
        marginLeft: '2px',
        verticalAlign: 'middle',
      }}
    />
  );
};

/**
 * 像素化密码显示组件
 */
export const PixelPassword: React.FC<{ length: number }> = ({ length }) => {
  return (
    <span style={{ fontFamily: 'monospace', letterSpacing: '2px' }}>
      {'*'.repeat(length)}
    </span>
  );
};