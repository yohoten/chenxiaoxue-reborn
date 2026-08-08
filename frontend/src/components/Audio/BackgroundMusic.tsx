/**
 * 背景音乐管理器
 * 根据情感状态动态切换背景音乐和音效
 */

import { useEffect, useRef, useState } from 'react';
import type { EmotionResult } from '../../types';

interface BackgroundMusicProps {
  emotion?: EmotionResult | null;
  enabled?: boolean;
  volume?: number; // 0-1
}

// 情感对应的音频配置
const EMOTION_AUDIO_CONFIG: Record<string, { 
  music?: string;      // 背景音乐
  soundEffect?: string; // 音效（可选）
  loop?: boolean;       // 是否循环
}> = {
  // 平静/中性 - 轻柔的背景音乐
  neutral: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 开心/喜悦 - 使用同一段音乐（后续可替换为不同版本）
  happy: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  joy: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 兴奋
  excited: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 惊讶 - 短促的音效（暂不使用）
  surprised: {
    // soundEffect: '/api/resources/file/sounds/effect_surprised.mp3',
    loop: false,
  },
  
  // 悲伤
  sad: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 愤怒
  angry: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 恐惧
  fear: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
  
  // 思考
  thinking: {
    music: '/api/resources/file/sounds/background_music.mp3',
    loop: true,
  },
};

export function BackgroundMusic({ 
  emotion = null, 
  enabled = true, 
  volume = 0.3 
}: BackgroundMusicProps) {
  const musicRef = useRef<HTMLAudioElement | null>(null);
  const effectRef = useRef<HTMLAudioElement | null>(null);
  const [currentEmotion, setCurrentEmotion] = useState<string>('neutral');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 初始化音频元素
  useEffect(() => {
    if (!enabled) return;

    // 创建背景音乐元素
    const music = new Audio();
    music.volume = volume;
    music.preload = 'metadata'; // 只预加载元数据，减少初始加载
    musicRef.current = music;

    // 创建音效元素
    const effect = new Audio();
    effect.volume = volume * 1.5; // 音效稍大一点
    effectRef.current = effect;

    // 监听播放状态
    music.addEventListener('playing', () => {
      setIsPlaying(true);
      setIsLoading(false);
    });
    music.addEventListener('pause', () => setIsPlaying(false));
    music.addEventListener('waiting', () => setIsLoading(true));
    music.addEventListener('canplaythrough', () => setIsLoading(false));

    return () => {
      music.pause();
      music.src = '';
      effect.pause();
      effect.src = '';
    };
  }, [enabled, volume]);

  // 根据情感切换音乐
  useEffect(() => {
    if (!enabled || !musicRef.current) return;

    const emotionKey = emotion?.emotion.toLowerCase() || 'neutral';
    
    // 如果情感没变化，不重复加载
    if (emotionKey === currentEmotion && isPlaying) return;
    
    const config = EMOTION_AUDIO_CONFIG[emotionKey] || EMOTION_AUDIO_CONFIG.neutral;
    setCurrentEmotion(emotionKey);

    // 如果没有音乐配置，不处理
    if (!config.music) return;

    // 淡出当前音乐
    if (musicRef.current && isPlaying) {
      fadeOut(musicRef.current, 500);
    }

    // 延迟后加载新音乐
    setTimeout(() => {
      if (config.music && musicRef.current) {
        setIsLoading(true);
        
        // 只在URL变化时才重新加载
        if (musicRef.current.src !== config.music) {
          musicRef.current.src = config.music;
          musicRef.current.loop = config.loop ?? true;
          
          // 显式加载
          musicRef.current.load();
        }
        
        // 尝试播放
        const playPromise = musicRef.current.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              // 播放成功，开始淡入
              fadeIn(musicRef.current!, 500);
            })
            .catch(err => {
              console.warn('音乐播放失败:', err);
              setIsLoading(false);
              
              // 如果是自动播放策略阻止，需要用户交互
              if (err.name === 'NotAllowedError') {
                console.log('需要用户交互才能播放音频');
              }
            });
        }
      }

      // 播放音效（如果有）
      if (config.soundEffect && effectRef.current) {
        effectRef.current.src = config.soundEffect;
        effectRef.current.loop = false;
        effectRef.current.play().catch(err => {
          console.warn('音效播放失败:', err);
        });
      }
    }, 500);
  }, [emotion, enabled, currentEmotion, isPlaying]);

  // 音量控制
  useEffect(() => {
    if (musicRef.current) {
      musicRef.current.volume = volume;
    }
    if (effectRef.current) {
      effectRef.current.volume = volume * 1.5;
    }
  }, [volume]);

  // 淡入效果
  const fadeIn = (audio: HTMLAudioElement, duration: number) => {
    audio.volume = 0;
    
    const steps = 20;
    const stepTime = duration / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      audio.volume = (step / steps) * volume;
      
      if (step >= steps) {
        clearInterval(timer);
      }
    }, stepTime);
  };

  // 淡出效果
  const fadeOut = (audio: HTMLAudioElement, duration: number) => {
    const startVolume = audio.volume;
    const steps = 20;
    const stepTime = duration / steps;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      audio.volume = startVolume * (1 - step / steps);
      
      if (step >= steps) {
        audio.pause();
        clearInterval(timer);
      }
    }, stepTime);
  };

  // 不渲染任何UI，纯逻辑组件
  return null;
}
