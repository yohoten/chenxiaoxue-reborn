/**
 * 像素风格按钮组件
 * 从原 PyQt5 PixelButton 迁移
 */

import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface PixelButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'danger' | 'nav' | 'secondary';
  active?: boolean;
  children: ReactNode;
}

export function PixelButton({
  variant = 'default',
  active = false,
  children,
  className = '',
  ...props
}: PixelButtonProps) {
  const variantClass = {
    default: '',
    primary: 'pixel-btn--primary',
    danger: 'pixel-btn--danger',
    nav: active ? 'pixel-btn--active' : '',
    secondary: '', // secondary 使用默认样式
  }[variant];

  return (
    <button
      className={`pixel-btn ${variantClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
