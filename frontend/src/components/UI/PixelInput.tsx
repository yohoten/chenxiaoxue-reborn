/**
 * 像素风格输入框组件
 */

import React from 'react';

interface PixelInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  glassEffect?: boolean;
}

const PixelInput: React.FC<PixelInputProps> = ({ 
  className = '', 
  glassEffect = false,
  ...props 
}) => {
  const baseClass = 'pixel-input';
  const glassClass = glassEffect ? 'glass-effect' : '';
  
  return (
    <input
      className={`${baseClass} ${glassClass} ${className}`.trim()}
      {...props}
    />
  );
};

export default PixelInput;
