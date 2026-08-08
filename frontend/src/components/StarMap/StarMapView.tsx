/**
 * 星图展示组件
 * 从旧项目迁移，优化为Web显示，支持全屏模式和缩略图导航
 */

import { useEffect, useState, useRef } from 'react';
import { getStarMaps } from '../../services/api';
import type { ResourceFile } from '../../types';
import { PixelButton } from '../Common/PixelButton';

interface StarMapViewProps {
  glassEffect?: boolean;
}

export function StarMapView({ glassEffect = false }: StarMapViewProps) {
  const [starMaps, setStarMaps] = useState<ResourceFile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [autoPlay, setAutoPlay] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // 加载星图列表
  useEffect(() => {
    getStarMaps()
      .then((data) => {
        if (data.star_maps.length > 0) {
          setStarMaps(data.star_maps);
        }
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('加载星图失败:', err);
        setIsLoading(false);
      });
  }, []);

  // 自动轮播
  useEffect(() => {
    if (!autoPlay || starMaps.length <= 1) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % starMaps.length);
    }, 8000); // 8秒切换一次

    return () => clearInterval(timer);
  }, [autoPlay, starMaps.length]);

  // 全屏切换
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // 切换到指定星图
  const selectStarMap = (index: number) => {
    setCurrentIndex(index);
    setAutoPlay(false); // 手动选择时暂停自动播放
  };

  // 上一张/下一张
  const previous = () => {
    setCurrentIndex((prev) => (prev - 1 + starMaps.length) % starMaps.length);
    setAutoPlay(false);
  };

  const next = () => {
    setCurrentIndex((prev) => (prev + 1) % starMaps.length);
    setAutoPlay(false);
  };

  if (isLoading) {
    return (
      <div className="star-map-container loading">
        <div className="pixel-text">加载中...</div>
      </div>
    );
  }

  if (starMaps.length === 0) {
    return (
      <div className="star-map-container empty">
        <div className="pixel-text">暂无星图资源</div>
      </div>
    );
  }

  const currentStarMap = starMaps[currentIndex];

  return (
    <div 
      ref={containerRef}
      className={`star-map-container ${isFullscreen ? 'fullscreen' : ''} ${glassEffect ? 'glass-effect' : ''}`}
    >
      {/* 主星图显示区 */}
      <div className="star-map-main">
        <img
          src={currentStarMap.path}
          alt={currentStarMap.name}
          className="star-map-image"
        />
        
        {/* 星图信息叠加层 */}
        <div className={`star-map-info ${glassEffect ? 'glass-effect' : ''}`}>
          <h3 className="star-map-title">{currentStarMap.name}</h3>
          <p className="star-map-index">
            {currentIndex + 1} / {starMaps.length}
          </p>
        </div>
      </div>

      {/* 控制按钮区 - 非全屏时显示 */}
      {!isFullscreen && (
        <div className={`star-map-controls ${glassEffect ? 'glass-effect' : ''}`}>
          {/* 导航按钮 */}
          <div className="control-buttons">
            <PixelButton onClick={previous}>
              ◀ 上一张
            </PixelButton>
            
            <PixelButton 
              onClick={() => setAutoPlay(!autoPlay)} 
              className={autoPlay ? 'pixel-btn--active' : ''}
            >
              {autoPlay ? '⏸ 暂停' : '▶ 播放'}
            </PixelButton>
            
            <PixelButton onClick={next}>
              下一张 ▶
            </PixelButton>
            
            <PixelButton onClick={toggleFullscreen}>
              ⛶ 全屏
            </PixelButton>
          </div>

          {/* 缩略图导航 */}
          <div className="thumbnail-nav">
            {starMaps.map((map, index) => (
              <button
                key={map.name}
                className={`thumbnail ${index === currentIndex ? 'active' : ''}`}
                onClick={() => selectStarMap(index)}
                title={map.name}
              >
                <img src={map.path} alt={map.name} />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 全屏模式下的退出提示 */}
      {isFullscreen && (
        <div className="fullscreen-hint">
          <PixelButton onClick={toggleFullscreen}>
            ✕ 退出全屏 (ESC)
          </PixelButton>
        </div>
      )}
    </div>
  );
}
