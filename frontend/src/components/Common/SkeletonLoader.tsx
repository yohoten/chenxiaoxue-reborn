// 骨架屏组件 - 提升加载体验
// 位置: frontend/src/components/Common/SkeletonLoader.tsx

import React from 'react';

interface SkeletonProps {
  type: 'text' | 'avatar' | 'bubble' | 'panel' | 'list';
  count?: number;
  width?: string | number;
  height?: string | number;
}

/**
 * 骨架屏加载组件
 * 在数据加载时显示占位动画，提升用户体验
 */
export const SkeletonLoader: React.FC<SkeletonProps> = ({
  type,
  count = 1,
  width,
  height,
}) => {
  const items = Array.from({ length: count });

  // 动画样式
  const shimmerStyle = {
    background: 'linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%)',
    backgroundSize: '200% 100%',
    animation: 'shimmer 1.5s infinite',
  };

  // 渲染不同类型
  const renderSkeleton = () => {
    switch (type) {
      case 'text':
        return (
          <div
            style={{
              height: height || '16px',
              width: width || '100%',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              marginBottom: '8px',
              ...shimmerStyle,
            }}
          />
        );

      case 'avatar':
        return (
          <div
            style={{
              width: width || '40px',
              height: height || '40px',
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              ...shimmerStyle,
            }}
          />
        );

      case 'bubble':
        return (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '12px', marginBottom: '8px' }}>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  flexShrink: 0,
                  ...shimmerStyle,
                }}
              />
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    height: '16px',
                    width: '30%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '4px',
                    marginBottom: '8px',
                    ...shimmerStyle,
                  }}
                />
                <div
                  style={{
                    height: height || '60px',
                    width: width || '80%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    ...shimmerStyle,
                  }}
                />
              </div>
            </div>
          </div>
        );

      case 'panel':
        return (
          <div
            style={{
              padding: '20px',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <div
              style={{
                height: '24px',
                width: '40%',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
                marginBottom: '16px',
                ...shimmerStyle,
              }}
            />
            {items.map((_, i) => (
              <div
                key={i}
                style={{
                  height: '40px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  marginBottom: '8px',
                  ...shimmerStyle,
                }}
              />
            ))}
          </div>
        );

      case 'list':
        return (
          <div>
            {items.map((_, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px',
                  marginBottom: '8px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    ...shimmerStyle,
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      height: '14px',
                      width: '60%',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '4px',
                      marginBottom: '6px',
                      ...shimmerStyle,
                    }}
                  />
                  <div
                    style={{
                      height: '12px',
                      width: '40%',
                      backgroundColor: 'rgba(255, 255, 255, 0.08)',
                      borderRadius: '4px',
                      ...shimmerStyle,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return <>{renderSkeleton()}</>;
};

// 添加全局动画
const style = document.createElement('style');
style.textContent = `
  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }
`;
document.head.appendChild(style);