/**
 * 登录页面 - 对话式设计（双面板主布局）- 像素风格强化版
 * 左侧：角色展示 + 状态信息
 * 右侧：对话引导式登录
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/auth';
import { PixelButton } from '../components/Common/PixelButton';
import { AnimatedBackground } from '../components/Background/AnimatedBackground';
import { PixelCharacter } from '../components/Common/PixelCharacter';
import { BlinkingCursor, useTypewriter } from '../components/Common/PixelArt';

const CHARACTER_IMAGE = '/assets/characters/20200922232838_082dc.gif';

interface ChatMsg {
  id: string;
  role: 'assistant' | 'user' | 'system';
  content: string;
  timestamp: number;
  isError?: boolean;
  isSuccess?: boolean;
}

type PanelMood = 'idle' | 'watching' | 'happy' | 'sad' | 'thinking';

const MOOD_LABELS: Record<PanelMood, string> = {
  idle: '等待接入...',
  watching: '正在注视着你 🔐',
  happy: '验证通过！✨',
  sad: '唔...再试试？',
  thinking: '思考中...',
};

const MOOD_CLASS: Record<PanelMood, string> = {
  idle: '',
  watching: 'character-panel--watching',
  happy: 'character-panel--happy',
  sad: 'character-panel--sad',
  thinking: 'character-panel--thinking',
};

const BADGE_CLASS: Record<PanelMood, string> = {
  idle: '',
  watching: '',
  happy: 'character-emotion-badge--happy',
  sad: 'character-emotion-badge--sad',
  thinking: 'character-emotion-badge--thinking',
};

const Login: React.FC = () => {
  const navigate = useNavigate();
  const msgEndRef = useRef<HTMLDivElement>(null);
  const pwRef = useRef<HTMLInputElement>(null);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'booting' | 'greeting' | 'password' | 'submitting'>('booting');
  const [capsLockOn, setCapsLockOn] = useState(false);
  const [panelMood, setPanelMood] = useState<PanelMood>('idle');
  const [shakeError, setShakeError] = useState(false);
  const [bootExiting, setBootExiting] = useState(false);
  const [bootSkippable, setBootSkippable] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // ── 实时时钟 ──────────────────────────────────────────
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (d: Date) =>
    `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;

  const formatDate = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

  // ── 启动文本动画 ──────────────────────────────────────
  const bootTexts = [
    '[系统初始化中...]',
    '[加载情感模块...]',
    '[连接MCP服务器...]',
    '[欢迎进入heademo终端]',
  ];
  const [bootIndex, setBootIndex] = useState(0);
  const { displayText: bootDisplay, isComplete: bootComplete } = useTypewriter(
    bootTexts[bootIndex],
    25
  );

  useEffect(() => {
    if (bootComplete && bootIndex < bootTexts.length - 1) {
      const timer = setTimeout(() => setBootIndex(prev => prev + 1), 400);
      return () => clearTimeout(timer);
    } else if (bootComplete && bootIndex === bootTexts.length - 1) {
      const timer = setTimeout(() => skipBoot(), 600);
      return () => clearTimeout(timer);
    }
  }, [bootComplete, bootIndex]);

  // 跳过按钮显示
  useEffect(() => {
    const timer = setTimeout(() => setBootSkippable(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  // 超时保护
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (step === 'booting') skipBoot();
    }, 4000);
    return () => clearTimeout(timeout);
  }, [step]);

  const skipBoot = useCallback(() => {
    setBootExiting(true);
    setTimeout(() => {
      setStep('greeting');
      setPanelMood('idle');
      setMessages([
        { id: 'env', role: 'system', content: '[系统启动完成] Chen筱雪已就绪', timestamp: Date.now() },
        { id: 'g1', role: 'assistant', content: '欢迎回来～ 请输入你的用户名开始吧 ✨', timestamp: Date.now() + 200 },
      ]);
    }, 400);
  }, []);

  const [messages, setMessages] = useState<ChatMsg[]>([]);
  useEffect(() => { msgEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // ── Caps Lock 检测 ────────────────────────────────────
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    setCapsLockOn(e.getModifierState('CapsLock'));
  }, []);

  // ── 用户名提交 ────────────────────────────────────────
  const handleUsernameSubmit = () => {
    const u = username.trim();
    if (!u) return;

    setMessages(prev => [
      ...prev,
      { id: `u-${Date.now()}`, role: 'user', content: u, timestamp: Date.now() },
      { id: `loading-${Date.now()}`, role: 'system', content: '__LOADING__', timestamp: Date.now() + 200 },
    ]);
    setPanelMood('thinking');

    setTimeout(() => {
      setMessages(prev => [
        ...prev.filter(m => m.content !== '__LOADING__'),
        { id: `a-${Date.now()}`, role: 'assistant', content: `好的，${u}！现在输入密码吧 🔐`, timestamp: Date.now() },
      ]);
      setStep('password');
      setPanelMood('watching');
      setTimeout(() => pwRef.current?.focus(), 100);
    }, 1200);
  };

  // ── 登录 ──────────────────────────────────────────────
  const handleLogin = async () => {
    if (!password.trim()) return;

    setMessages(prev => [
      ...prev,
      { id: `upw-${Date.now()}`, role: 'user', content: '*'.repeat(password.length), timestamp: Date.now() },
      { id: `al-${Date.now()}`, role: 'assistant', content: '正在验证身份...', timestamp: Date.now() + 200 },
    ]);

    setLoading(true);
    setError('');
    setPanelMood('thinking');

    try {
      await authAPI.login({ username: username.trim(), password });

      // 登录成功
      setPanelMood('happy');
      setMessages(prev => [
        ...prev,
        { id: 'ok', role: 'assistant', content: '🎉 身份验证通过！欢迎回来～', timestamp: Date.now(), isSuccess: true },
      ]);

      setTimeout(() => navigate('/'), 800);
    } catch (err: any) {
      setLoading(false);
      setPanelMood('sad');
      setShakeError(true);

      const msg = err.response?.status === 401
        ? '唔…密码好像不太对，再试试？（她歪头看着你）😅'
        : err.response?.data?.detail || '登录失败了，稍后再试吧～';

      setError(msg);
      setMessages(prev => [
        ...prev,
        { id: `e-${Date.now()}`, role: 'assistant', content: msg, timestamp: Date.now(), isError: true },
      ]);

      setTimeout(() => {
        setShakeError(false);
        setPanelMood('watching');
      }, 1500);
      setTimeout(() => pwRef.current?.focus(), 100);
    }
  };

  const handleEnterKey = (e: React.KeyboardEvent, fn: () => void) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); fn(); }
  };

  // ── 左侧面板时钟 ──────────────────────────────────────
  const renderLeftPanelClock = () => (
    <div className="panel-clock-area">
      <div className="led-clock">{formatTime(currentTime)}</div>
      <div className="led-clock__date">{formatDate(currentTime)}</div>
    </div>
  );

  // ── 渲染输入区域 ──────────────────────────────────────
  const renderInputArea = () => {
    if (step === 'greeting') {
      return (
        <div className="auth-chat-input-row auth-step-transition">
          <input
            className="pixel-input pixel-input-enhanced"
            type="text"
            value={username}
            onChange={e => { setUsername(e.target.value); setError(''); }}
            onKeyDown={e => handleEnterKey(e, handleUsernameSubmit)}
            placeholder="输入用户名..."
            autoFocus
          />
          <PixelButton variant="primary" onClick={handleUsernameSubmit} disabled={!username.trim()}>
            发送 ➤
          </PixelButton>
        </div>
      );
    }

    return (
      <div className="auth-chat-input-row auth-step-transition">
        <div style={{ position: 'relative', flex: 1 }}>
          {capsLockOn && <div className="capslock-warning">⚠ CAPS LOCK ON</div>}
          <input
            ref={pwRef}
            className={`pixel-input pixel-input-enhanced ${shakeError ? 'auth-shake' : ''}`}
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => { setPassword(e.target.value); setError(''); }}
            onKeyDown={e => { handleKeyDown(e); handleEnterKey(e, handleLogin); }}
            placeholder="输入密码..."
            autoFocus
            style={{ width: '100%', paddingRight: 36 }}
          />
          <button
            type="button"
            className="pixel-eye-btn"
            onClick={() => setShowPassword(v => !v)}
            title={showPassword ? '隐藏密码' : '显示密码'}
          >
            {showPassword ? '⊘' : '◉'}
          </button>
        </div>
        <PixelButton variant="primary" onClick={handleLogin} disabled={!password.trim() || loading}>
          {loading ? '验证中...' : '🔐 登录'}
        </PixelButton>
      </div>
    );
  };

  // ── 启动界面 ──────────────────────────────────────────
  if (step === 'booting') {
    return (
      <div className={`app-container crt-effect ${bootExiting ? 'boot-fade-out' : ''}`}>
        <AnimatedBackground interval={30000} />

        <div style={{
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          height: '100vh', flexDirection: 'column', gap: '20px',
        }}>
          <div className="ascii-art">
{`
 ██████╗██╗   ██╗██████╗ ███████╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
╚██████╗   ██║   ██████╔╝███████╗██║  ██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝
`}
          </div>

          <div className="system-boot-text">
            {bootDisplay}
            <BlinkingCursor />
          </div>

          <div className="developer-credit">
            developed by yohoten <span className="version-led">R1.0.0</span>
          </div>

          {bootSkippable && (
            <button className="boot-skip-hint" onClick={skipBoot}>
              [ 点击任意位置跳过启动 ]
            </button>
          )}
        </div>
      </div>
    );
  }

  // ── 主界面 ────────────────────────────────────────────
  return (
    <div className="app-container crt-effect auth-panel-enter">
      <AnimatedBackground interval={30000} />

      <div className="main-layout">
        {/* ── 左侧面板 ────────────────────────────── */}
        <div className="left-panel pixel-border-box">
          {/* 实时时钟 */}
          {renderLeftPanelClock()}

          {/* 角色展示 */}
          <div className={`character-panel pixel-photo-frame ${MOOD_CLASS[panelMood]}`}>
            <img src={CHARACTER_IMAGE} alt="ChenXiaoxue" />
            <div className="character-panel__overlay" />
            <div className={`character-emotion-badge ${BADGE_CLASS[panelMood]}`}>
              {MOOD_LABELS[panelMood]}
            </div>
          </div>

          {/* 状态信息 */}
          <div className="status-panel">
            <div className="pixel-title" style={{ fontSize: 16, textAlign: 'center', marginBottom: 8 }}>
              🌸 Chen筱雪
            </div>
            <div className="status-panel__emotion">
              <span className="pixel-subtitle">基于FastAPI + MCP的多模型情感互动heademo</span>
              <br /><br />
              <span className="developer-credit">
                developed by yohoten <span className="version-led">R1.0.0</span>
              </span>
            </div>
          </div>

          {/* 注册链接 */}
          <div className="auth-sidebar-footer">
            <span className="pixel-text--secondary" style={{ fontSize: 11 }}>还没有账号？</span>
            <Link to="/register" className="register-pixel-btn">立即注册 →</Link>
          </div>
        </div>

        {/* ── 右侧对话面板 ────────────────────────── */}
        <div className="chat-panel pixel-border-box">
          <div className="auth-chat-header">
            <span className="terminal-prompt">💬 登录终端</span>
            <span className="pixel-text--secondary" style={{ fontSize: 11 }}>
              {step === 'greeting' ? '请输入用户名' : '请输入密码'}
            </span>
          </div>

          {/* 消息列表 */}
          <div className="message-list">
            {messages.map((msg, i) => {
              if (msg.content === '__LOADING__') {
                return (
                  <div key={msg.id} className="loading-indicator--pixel-enhanced">
                    <PixelCharacter action="thinking" size={24} />
                    <span>检索档案中</span>
                    <span className="loading-dots-animated">
                      <span className="loading-dot" />
                      <span className="loading-dot" />
                      <span className="loading-dot" />
                    </span>
                  </div>
                );
              }

              const bubbleClass = [
                'message-bubble',
                `message-bubble--${msg.role}`,
                'message-bubble--pixel',
                msg.isError ? 'message-bubble--error' : '',
                msg.isSuccess ? 'message-bubble--success' : '',
                i === messages.length - 1 ? 'auth-bounce-in' : '',
                msg.isError ? 'auth-shake' : '',
              ].filter(Boolean).join(' ');

              return (
                <div key={msg.id} className={bubbleClass}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3, fontSize: 10, opacity: 0.55 }}>
                    <span>{msg.role === 'assistant' ? '🤖 Chen筱雪' : msg.role === 'user' ? '👤 你' : '💬 系统'}</span>
                    <span>{new Date(msg.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: 13, lineHeight: 1.6 }}>
                    {msg.content}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="loading-indicator--pixel-enhanced">
                <PixelCharacter action="walking" size={24} />
                <span>验证中</span>
                <span className="loading-dots-animated">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </span>
              </div>
            )}

            <div ref={msgEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="input-area">
            {renderInputArea()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
