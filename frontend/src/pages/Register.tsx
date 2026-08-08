/**
 * 注册页面 - 对话式设计（双面板主布局）- 像素风格强化版
 * 左侧：角色展示 + 状态信息
 * 右侧：逐步引导注册
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

type PanelMood = 'idle' | 'curious' | 'watching' | 'happy' | 'sad' | 'thinking';
type Step = 'booting' | 'greeting' | 'username' | 'password' | 'confirm' | 'optional' | 'submitting';

const MOOD_LABELS: Record<PanelMood, string> = {
  idle: '等待新冒险者...',
  curious: '好奇地打量着你 👀',
  watching: '认真记录中... 📝',
  happy: '档案创建成功！🎉',
  sad: '唔...出了点问题',
  thinking: '处理中...',
};

const MOOD_CLASS: Record<PanelMood, string> = {
  idle: '',
  curious: 'character-panel--watching',
  watching: 'character-panel--watching',
  happy: 'character-panel--happy',
  sad: 'character-panel--sad',
  thinking: 'character-panel--thinking',
};

const BADGE_CLASS: Record<PanelMood, string> = {
  idle: '',
  curious: '',
  watching: '',
  happy: 'character-emotion-badge--happy',
  sad: 'character-emotion-badge--sad',
  thinking: 'character-emotion-badge--thinking',
};

const getPanelMood = (step: Step): PanelMood => {
  switch (step) {
    case 'greeting': return 'idle';
    case 'username': return 'curious';
    case 'password':
    case 'confirm': return 'watching';
    case 'optional': return 'curious';
    case 'submitting': return 'thinking';
    default: return 'idle';
  }
};

// ── 密码强度计算 ────────────────────────────────────────
const getPasswordStrength = (pw: string): { score: 0 | 1 | 2 | 3; label: string } => {
  if (!pw) return { score: 0, label: '' };
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  if (score <= 2) return { score: 1, label: '弱' };
  if (score <= 3) return { score: 2, label: '中' };
  return { score: 3, label: '强' };
};

const STRENGTH_COLORS: Record<number, string> = {
  0: 'var(--text-secondary)',
  1: 'var(--error)',
  2: 'var(--warning)',
  3: 'var(--success)',
};

const Register: React.FC = () => {
  const navigate = useNavigate();
  const msgEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({ username: '', password: '', confirmPassword: '', email: '', nickname: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<Step>('booting');
  const [showPassword, setShowPassword] = useState(false);
  const [capsLockOn, setCapsLockOn] = useState(false);
  const [panelMood, setPanelMood] = useState<PanelMood>('idle');
  const [shakeError, setShakeError] = useState(false);
  const [bootExiting, setBootExiting] = useState(false);
  const [bootSkippable, setBootSkippable] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  const pwStrength = getPasswordStrength(form.password);

  // ── 实时时钟 ──────────────────────────────────────────
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (d: Date) =>
    `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
  const formatDate = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

  // ── 启动序列 ──────────────────────────────────────────
  const bootTexts = [
    '[系统初始化中...]',
    '[加载用户模块...]',
    '[准备创建新档案...]',
    '[欢迎进入注册终端]',
  ];
  const [bootIndex, setBootIndex] = useState(0);
  const { displayText: bootDisplay, isComplete: bootComplete } = useTypewriter(bootTexts[bootIndex], 25);

  useEffect(() => {
    if (bootComplete && bootIndex < bootTexts.length - 1) {
      const timer = setTimeout(() => setBootIndex(prev => prev + 1), 400);
      return () => clearTimeout(timer);
    } else if (bootComplete && bootIndex === bootTexts.length - 1) {
      const timer = setTimeout(() => skipBoot(), 600);
      return () => clearTimeout(timer);
    }
  }, [bootComplete, bootIndex]);

  useEffect(() => {
    const timer = setTimeout(() => setBootSkippable(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => { if (step === 'booting') skipBoot(); }, 4000);
    return () => clearTimeout(timeout);
  }, [step]);

  const skipBoot = useCallback(() => {
    setBootExiting(true);
    setTimeout(() => {
      setStep('greeting');
      setPanelMood('idle');
      setMessages([
        { id: 'env', role: 'system', content: '[系统就绪] Chen筱雪等待新冒险者...', timestamp: Date.now() },
        { id: 'g1', role: 'assistant', content: '嗨！我是Chen筱雪～ 🌸', timestamp: Date.now() + 200 },
        { id: 'g2', role: 'assistant', content: '啊，是新来的冒险者？那我先帮你建个档案吧！✨\n先告诉我你想要的用户名～', timestamp: Date.now() + 500 },
      ]);
    }, 400);
  }, []);

  const [messages, setMessages] = useState<ChatMsg[]>([]);
  useEffect(() => { msgEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { setTimeout(() => inputRef.current?.focus(), 120); }, [step]);

  // ── Caps Lock 检测 ────────────────────────────────────
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    setCapsLockOn(e.getModifierState('CapsLock'));
  }, []);

  // ── 校验 ──────────────────────────────────────────────
  const validate = (): boolean => {
    if (step === 'username' && (form.username.length < 3 || form.username.length > 20)) {
      setError('用户名需要 3-20 个字符哦～'); return false;
    }
    if (step === 'password' && form.password.length < 6) {
      setError('密码至少需要 6 个字符哦～'); return false;
    }
    if (step === 'confirm' && form.password !== form.confirmPassword) {
      setError('两次输入的密码不一样呢 😅'); return false;
    }
    return true;
  };

  const userLabel = (): string => {
    switch (step) {
      case 'username': return form.username;
      case 'password': return '*'.repeat(form.password.length);
      case 'confirm': return '*'.repeat(form.confirmPassword.length);
      case 'optional': {
        const parts: string[] = [];
        if (form.nickname) parts.push(`昵称: ${form.nickname}`);
        if (form.email) parts.push(`邮箱: ${form.email}`);
        return parts.length ? parts.join(' | ') : '跳过选填';
      }
      default: return '';
    }
  };

  const nextStep = (): Step => {
    switch (step) {
      case 'greeting': return 'username';
      case 'username': return 'password';
      case 'password': return 'confirm';
      case 'confirm': return 'optional';
      case 'optional': return 'submitting';
      default: return 'submitting';
    }
  };

  const stepPrompt = (s: Step): string => {
    switch (s) {
      case 'username': return '好的！请输入你想要的用户名吧～（3-20个字符）';
      case 'password': return '设置一个密码吧 🔐（至少6个字符）';
      case 'confirm': return '再输入一次确认～';
      case 'optional': return '还想补充点信息吗？😊\n昵称和邮箱都是选填的～';
      default: return '';
    }
  };

  const goNext = () => {
    if (!validate()) {
      setShakeError(true);
      setTimeout(() => setShakeError(false), 500);
      return;
    }
    setError('');
    setMessages(prev => [...prev, { id: `u-${Date.now()}`, role: 'user', content: userLabel(), timestamp: Date.now() }]);
    const ns = nextStep();
    if (ns === 'submitting') { doRegister(); return; }

    setPanelMood('thinking');

    if (ns === 'password' || ns === 'confirm') {
      setMessages(prev => [
        ...prev,
        { id: `loading-${Date.now()}`, role: 'system', content: '__LOADING__', timestamp: Date.now() + 200 },
      ]);
      setTimeout(() => {
        setMessages(prev => [
          ...prev.filter(m => m.content !== '__LOADING__'),
          { id: `a-${Date.now()}`, role: 'assistant', content: stepPrompt(ns), timestamp: Date.now() },
        ]);
        setStep(ns);
        setPanelMood(getPanelMood(ns));
      }, 1000);
    } else {
      setTimeout(() => {
        setMessages(prev => [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: stepPrompt(ns), timestamp: Date.now() }]);
        setStep(ns);
        setPanelMood(getPanelMood(ns));
      }, 400);
    }
  };

  const doRegister = async () => {
    setMessages(prev => [...prev, { id: 'reg', role: 'assistant', content: '正在创建你的账号... ✨', timestamp: Date.now() }]);
    setStep('submitting');
    setLoading(true);
    setPanelMood('thinking');

    try {
      await authAPI.register({
        username: form.username,
        email: form.email || undefined,
        password: form.password,
        nickname: form.nickname || undefined,
      });

      setPanelMood('happy');
      setMessages(prev => [
        ...prev,
        { id: 'ok', role: 'assistant', content: `🎉 档案创建成功！${form.nickname || form.username}～\n即将跳转到登录页...`, timestamp: Date.now(), isSuccess: true },
      ]);
      setTimeout(() => navigate('/login', { state: { message: '注册成功！请登录' } }), 1200);
    } catch (err: any) {
      setLoading(false);
      setPanelMood('sad');
      setShakeError(true);

      let msg = '注册失败了，再试试吧～ 😅';
      if (err.response?.status === 400) {
        if (err.response.data.detail.includes('Username')) { msg = '用户名已被注册啦，换一个吧～'; setStep('username'); }
        else if (err.response.data.detail.includes('Email')) { msg = '邮箱已被注册啦～'; setStep('optional'); }
        else msg = err.response.data.detail;
      }
      setError(msg);
      setMessages(prev => [
        ...prev,
        { id: `e-${Date.now()}`, role: 'assistant', content: msg, timestamp: Date.now(), isError: true },
      ]);

      setTimeout(() => {
        setShakeError(false);
        setPanelMood(getPanelMood(step));
      }, 1500);
    }
  };

  const handleEnterKey = (e: React.KeyboardEvent, fn: () => void) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); fn(); }
  };

  const startRegister = () => {
    const ns = nextStep();
    setMessages(prev => [...prev, { id: `go-${Date.now()}`, role: 'user', content: '开始注册 ✨', timestamp: Date.now() }]);
    setTimeout(() => {
      setMessages(prev => [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: stepPrompt(ns), timestamp: Date.now() }]);
      setStep(ns);
      setPanelMood(getPanelMood(ns));
    }, 400);
  };

  // ── 密码强度指示条 ────────────────────────────────────
  const renderPasswordStrength = () => {
    if (step !== 'password' || !form.password) return null;
    const segClass = (n: number) => {
      if (pwStrength.score === 1) return n === 1 ? 'active' : '';
      if (pwStrength.score === 2) return n <= 2 ? 'active' : '';
      if (pwStrength.score === 3) return 'active';
      return '';
    };
    return (
      <div className="password-strength">
        <div className={`password-strength__seg password-strength__seg--weak ${segClass(1)}`} />
        <div className={`password-strength__seg password-strength__seg--medium ${segClass(2)}`} />
        <div className={`password-strength__seg password-strength__seg--strong ${segClass(3)}`} />
        <span className="password-strength__label" style={{ color: STRENGTH_COLORS[pwStrength.score], minWidth: 20 }}>
          {pwStrength.label}
        </span>
      </div>
    );
  };

  // ── 左侧面板时钟 ──────────────────────────────────────
  const renderLeftPanelClock = () => (
    <div className="panel-clock-area">
      <div className="led-clock">{formatTime(currentTime)}</div>
      <div className="led-clock__date">{formatDate(currentTime)}</div>
    </div>
  );

  // ── 渲染输入 ──────────────────────────────────────────
  const renderInput = () => {
    const isPwStep = step === 'password' || step === 'confirm';
    const pwFieldValue = step === 'password' ? form.password : form.confirmPassword;
    const pwFieldOnChange = (v: string) => {
      if (step === 'password') setForm(f => ({ ...f, password: v }));
      else setForm(f => ({ ...f, confirmPassword: v }));
    };

    switch (step) {
      case 'greeting':
        return (
          <div className="auth-chat-input-row auth-step-transition" style={{ justifyContent: 'center' }}>
            <PixelButton variant="primary" onClick={startRegister} style={{ flex: 1, maxWidth: 260 }} className="pixel-btn-retro">
              ✨ 开始注册
            </PixelButton>
          </div>
        );
      case 'username':
        return (
          <div className="auth-chat-input-row auth-step-transition">
            <input ref={inputRef} className="pixel-input pixel-input-enhanced" type="text" value={form.username}
              onChange={e => { setForm(f => ({ ...f, username: e.target.value })); setError(''); }}
              onKeyDown={e => handleEnterKey(e, goNext)} placeholder="输入用户名（3-20字符）" autoFocus />
            <PixelButton variant="primary" onClick={goNext} disabled={!form.username.trim()} className="pixel-btn-retro">下一步 ➤</PixelButton>
          </div>
        );
      case 'password':
        return (
          <div>
            <div className={`auth-chat-input-row auth-step-transition ${shakeError ? 'auth-shake' : ''}`}>
              <div style={{ position: 'relative', flex: 1 }}>
                {capsLockOn && <div className="capslock-warning">⚠ CAPS LOCK ON</div>}
                <input ref={inputRef} className="pixel-input pixel-input-enhanced"
                  type={showPassword ? 'text' : 'password'} value={form.password}
                  onChange={e => { setForm(f => ({ ...f, password: e.target.value })); setError(''); }}
                  onKeyDown={e => { handleKeyDown(e); handleEnterKey(e, goNext); }}
                  placeholder="设置密码（至少6位）" autoFocus
                  style={{ width: '100%', paddingRight: 36 }} />
                <button type="button" className="pixel-eye-btn"
                  onClick={() => setShowPassword(v => !v)}
                  title={showPassword ? '隐藏密码' : '显示密码'}>
                  {showPassword ? '⊘' : '◉'}
                </button>
              </div>
              <PixelButton variant="primary" onClick={goNext} disabled={form.password.length < 6} className="pixel-btn-retro">下一步 ➤</PixelButton>
            </div>
            {renderPasswordStrength()}
          </div>
        );
      case 'confirm':
        return (
          <div className={`auth-chat-input-row auth-step-transition ${shakeError ? 'auth-shake' : ''}`}>
            <div style={{ position: 'relative', flex: 1 }}>
              {capsLockOn && <div className="capslock-warning">⚠ CAPS LOCK ON</div>}
              <input ref={inputRef} className="pixel-input pixel-input-enhanced"
                type={showPassword ? 'text' : 'password'} value={form.confirmPassword}
                onChange={e => { setForm(f => ({ ...f, confirmPassword: e.target.value })); setError(''); }}
                onKeyDown={e => { handleKeyDown(e); handleEnterKey(e, goNext); }}
                placeholder="再次输入密码" autoFocus
                style={{ width: '100%', paddingRight: 36 }} />
              <button type="button" className="pixel-eye-btn"
                onClick={() => setShowPassword(v => !v)}
                title={showPassword ? '隐藏密码' : '显示密码'}>
                {showPassword ? '⊘' : '◉'}
              </button>
            </div>
            <PixelButton variant="primary" onClick={goNext} disabled={!form.confirmPassword.trim()} className="pixel-btn-retro">确认 ➤</PixelButton>
          </div>
        );
      case 'optional':
        return (
          <div className="auth-step-transition">
            <div className="auth-chat-optional-form">
              <div className="auth-chat-input-row">
                <input ref={inputRef} className="pixel-input pixel-input-enhanced" type="text" value={form.nickname}
                  onChange={e => setForm(f => ({ ...f, nickname: e.target.value }))} placeholder="昵称（选填）" />
              </div>
              <div className="auth-chat-input-row">
                <input className="pixel-input pixel-input-enhanced" type="email" value={form.email}
                  onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="邮箱（选填）" />
              </div>
              <div className="auth-chat-input-row">
                <PixelButton variant="primary" onClick={doRegister} disabled={loading} className="pixel-btn-retro" style={{ flex: 1 }}>
                  {loading ? '注册中...' : '✨ 完成注册'}
                </PixelButton>
                <PixelButton variant="secondary" onClick={doRegister} disabled={loading} className="pixel-btn-retro">跳过</PixelButton>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // ── 启动界面 ──────────────────────────────────────────
  if (step === 'booting') {
    return (
      <div className={`app-container crt-effect ${bootExiting ? 'boot-fade-out' : ''}`}>
        <AnimatedBackground interval={30000} />
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column', gap: '20px' }}>
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
          <div className="system-boot-text">{bootDisplay}<BlinkingCursor /></div>
          <div className="developer-credit">developed by yohoten <span className="version-led">R1.0.0</span></div>
          {bootSkippable && <button className="boot-skip-hint" onClick={skipBoot}>[ 点击任意位置跳过启动 ]</button>}
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
          {renderLeftPanelClock()}

          <div className={`character-panel pixel-photo-frame ${MOOD_CLASS[panelMood]}`}>
            <img src={CHARACTER_IMAGE} alt="ChenXiaoxue" />
            <div className="character-panel__overlay" />
            <div className={`character-emotion-badge ${BADGE_CLASS[panelMood]}`}>
              {MOOD_LABELS[panelMood]}
            </div>
          </div>

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

          <div className="auth-sidebar-footer">
            <span className="pixel-text--secondary" style={{ fontSize: 11 }}>已有账号？</span>
            <Link to="/login" className="register-pixel-btn">立即登录 →</Link>
          </div>
        </div>

        {/* ── 右侧对话面板 ────────────────────────── */}
        <div className="chat-panel pixel-border-box">
          <div className="auth-chat-header">
            <span className="terminal-prompt">💬 注册终端</span>
            <span className="pixel-text--secondary" style={{ fontSize: 11 }}>
              {step === 'greeting' ? '欢迎注册' :
               step === 'username' ? '设置用户名' :
               step === 'password' ? '设置密码' :
               step === 'confirm' ? '确认密码' :
               step === 'optional' ? '补充信息（选填）' : '提交中...'}
            </span>
          </div>

          {/* 步骤指示器 */}
          {step !== 'submitting' && (
            <div style={{
              display: 'flex', justifyContent: 'center', gap: 6,
              padding: '8px 16px', borderBottom: '1px solid var(--border-color)',
              fontSize: 11, fontFamily: 'var(--font-pixel-en)',
            }}>
              {[
                { s: 'greeting' as Step, label: '欢迎' },
                { s: 'username' as Step, label: '账号' },
                { s: 'password' as Step, label: '密码' },
                { s: 'confirm' as Step, label: '确认' },
                { s: 'optional' as Step, label: '完成' },
              ].map(({ s, label }, i) => {
                const steps: Step[] = ['greeting', 'username', 'password', 'confirm', 'optional'];
                const idx = steps.indexOf(step as Step);
                const isActive = idx >= 0 && steps.indexOf(s as Step) === idx;
                const isDone = idx >= 0 && steps.indexOf(s as Step) < idx;
                return (
                  <React.Fragment key={s}>
                    {i > 0 && (
                      <span style={{ color: isDone ? 'var(--accent-primary)' : 'var(--border-color)' }}>──</span>
                    )}
                    <span style={{
                      color: isActive ? 'var(--accent-primary)' : isDone ? 'var(--success)' : 'var(--text-secondary)',
                      fontWeight: isActive ? 'bold' : 'normal',
                    }}>
                      {isDone ? '●' : isActive ? '◉' : '○'} {label}
                    </span>
                  </React.Fragment>
                );
              })}
            </div>
          )}

          {/* 消息列表 */}
          <div className="message-list">
            {messages.map((msg, i) => {
              if (msg.content === '__LOADING__') {
                return (
                  <div key={msg.id} className="loading-indicator--pixel-enhanced">
                    <PixelCharacter action="thinking" size={24} />
                    <span>验证档案</span>
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
                i === messages.length - 1 && !msg.isError ? 'auth-bounce-in' : '',
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
                <span>创建档案中</span>
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
          {step !== 'submitting' && (
            <div className="input-area">
              {renderInput()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Register;
