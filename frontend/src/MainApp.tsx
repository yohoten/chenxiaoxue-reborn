import React, { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { AnimatedBackground } from './components/Background/AnimatedBackground';
import { EmotionIndicator } from './components/Emotion/EmotionIndicator';
import { ECGStatusBar } from './components/Emotion/ECGStatusBar';
import { OptimizedMessageList } from './components/Chat/OptimizedMessageList';
import { ChatInput } from './components/Chat/ChatInput';
import { PixelButton } from './components/Common/PixelButton';
import { BackgroundMusic } from './components/Audio/BackgroundMusic';
import UserMenu from './components/User/UserMenu';
import { useNavigate } from 'react-router-dom';
import { useChat } from './hooks/useChat';
import { useMCP } from './hooks/useMCP';
import { useTheme } from './hooks/useTheme';
import { authAPI } from './services/auth';
import { getChatHistory } from './services/api';
import type { ThemeType } from './hooks/useTheme';
import type { Conversation, Message } from './types';

// Tab 组件按需加载（chat 是默认 tab，保持同步加载）
const HistoryPanel = lazy(() => import('./components/History/HistoryPanel').then(m => ({ default: m.HistoryPanel })));
const DreamSpace = lazy(() => import('./components/Dream/DreamSpace').then(m => ({ default: m.DreamSpace })));
const StarMapView = lazy(() => import('./components/StarMap/StarMapView').then(m => ({ default: m.StarMapView })));
const ComponentShowcase = lazy(() => import('./components/Showcase/ComponentShowcase').then(m => ({ default: m.ComponentShowcase })));
const HumanizerPanel = lazy(() => import('./components/Humanizer/HumanizerPanel').then(m => ({ default: m.HumanizerPanel })));

const TabFallback: React.FC = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: '#888' }}>
    加载中...
  </div>
);

type TabId = 'chat' | 'history' | 'settings' | 'dream' | 'starmap' | 'showcase' | 'humanizer';

// ── 设置子标签页类型 ──────────────────────────────────────
type SettingsTab = 'appearance' | 'chat' | 'audio' | 'about';

const SETTINGS_TABS: { id: SettingsTab; label: string }[] = [
  { id: 'appearance', label: '🎨 外观' },
  { id: 'chat', label: '💬 对话' },
  { id: 'audio', label: '🔊 音频' },
  { id: 'about', label: 'ℹ️ 关于' },
];

interface SettingsPanelProps {
  glassEffect: boolean;
  mcpStatus: { connected: boolean };
  typewriterEffect: boolean;
  setTypewriterEffect: (v: boolean) => void;
  crtEffect: boolean;
  setCrtEffect: (v: boolean) => void;
  bgMusicEnabled: boolean;
  setBgMusicEnabled: (v: boolean) => void;
  setGlassEffect: (v: boolean) => void;
  currentTheme: string;
  onThemeChange: (t: ThemeType) => void;
  themes: { id: ThemeType; name: string }[];
}

function SettingsPanel(props: SettingsPanelProps) {
  const [subTab, setSubTab] = useState<SettingsTab>('appearance');
  const {
    glassEffect, mcpStatus, typewriterEffect, setTypewriterEffect,
    crtEffect, setCrtEffect, bgMusicEnabled, setBgMusicEnabled,
    setGlassEffect, currentTheme, onThemeChange, themes,
  } = props;

  const SwitchBtn = ({ on, label, onClick }: { on: boolean; label: string; onClick: () => void }) => (
    <PixelButton onClick={onClick} className={on ? 'pixel-btn--active' : ''}>
      {on ? `✓ ${label}` : `✗ ${label}`}
    </PixelButton>
  );

  return (
    <div className="settings-panel">
      <h2 className="pixel-title">⚙️ 设置</h2>

      {/* 设置子标签 */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
        {SETTINGS_TABS.map(t => (
          <PixelButton
            key={t.id}
            variant="nav"
            active={subTab === t.id}
            onClick={() => setSubTab(t.id)}
            style={{ fontSize: 11, padding: '6px 12px', minWidth: 0 }}
          >
            {t.label}
          </PixelButton>
        ))}
      </div>

      <div className={`settings-group ${glassEffect ? 'glass-effect' : ''}`}>

        {subTab === 'appearance' && (
          <>
            <h3 className="pixel-subtitle">主题</h3>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
              {themes.map(t => (
                <PixelButton
                  key={t.id}
                  variant="nav"
                  active={currentTheme === t.id}
                  onClick={() => onThemeChange(t.id)}
                  style={{ fontSize: 10, padding: '5px 10px', minWidth: 0 }}
                >
                  {t.name}
                </PixelButton>
              ))}
            </div>

            <h3 className="pixel-subtitle">效果</h3>
            <div className="settings-row">
              <label>毛玻璃</label>
              <SwitchBtn on={glassEffect} label="已开启" onClick={() => setGlassEffect(!glassEffect)} />
            </div>
            <div className="settings-row">
              <label>CRT 滤镜</label>
              <SwitchBtn on={crtEffect} label="已开启" onClick={() => setCrtEffect(!crtEffect)} />
            </div>
          </>
        )}

        {subTab === 'chat' && (
          <>
            <h3 className="pixel-subtitle">模型</h3>
            <div className="settings-row">
              <label>路由模式</label>
              <span className="pixel-text">自动路由</span>
            </div>
            <div className="settings-row">
              <label>API 模式</label>
              <span className="pixel-text">{mcpStatus.connected ? 'MCP 协议' : '直接 API'}</span>
            </div>

            <h3 className="pixel-subtitle">显示</h3>
            <div className="settings-row">
              <label>打字机效果</label>
              <SwitchBtn on={typewriterEffect} label="已开启" onClick={() => setTypewriterEffect(!typewriterEffect)} />
            </div>

            <h3 className="pixel-subtitle">快捷键</h3>
            <div className="settings-row">
              <label>发送消息</label>
              <span className="pixel-text" style={{ fontFamily: 'var(--font-pixel-en)' }}>Enter</span>
            </div>
            <div className="settings-row">
              <label>清空对话</label>
              <span className="pixel-text" style={{ fontFamily: 'var(--font-pixel-en)' }}>Ctrl + K</span>
            </div>
          </>
        )}

        {subTab === 'audio' && (
          <>
            <h3 className="pixel-subtitle">背景音乐</h3>
            <div className="settings-row">
              <label>状态</label>
              <SwitchBtn on={bgMusicEnabled} label="已开启" onClick={() => setBgMusicEnabled(!bgMusicEnabled)} />
            </div>
            <div className="settings-row">
              <label>说明</label>
              <span className="pixel-text--secondary" style={{ fontSize: 10 }}>
                根据情感动态切换音乐
              </span>
            </div>
          </>
        )}

        {subTab === 'about' && (
          <>
            <h3 className="pixel-subtitle">Chen筱雪 Reborn</h3>
            <div className="settings-row">
              <label>版本</label>
              <span className="pixel-text">1.0.0</span>
            </div>
            <div className="settings-row">
              <label>架构</label>
              <span className="pixel-text">FastAPI + React + Tauri</span>
            </div>
            <div className="settings-row">
              <label>作者</label>
              <span className="pixel-text">developed by yohoten</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// 终端风格时钟
function TerminalClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{
      textAlign: 'center', padding: '4px 0 2px',
      fontFamily: '"VT323", monospace', fontSize: 13,
      color: 'var(--text-secondary)', opacity: 0.7,
      letterSpacing: '1px',
    }}>
      {time.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' })}
      {' '}
      {time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
    </div>
  );
}

// 左面板下半区 Tab：对话 / 交互
type SidebarPanel = 'chat' | 'interaction';

const INTERACTION_ITEMS: { id: TabId; icon: string; label: string }[] = [
  { id: 'dream', icon: '🌙', label: '梦境' },
  { id: 'starmap', icon: '✨', label: '星图' },
  { id: 'showcase', icon: '🎨', label: '组件' },
  { id: 'humanizer', icon: '✍️', label: '人性化' },
];

export default function MainApp() {
  const navigate = useNavigate();
  const { messages, isProcessing, sendMessage, clearMessages, setMessages, currentEmotion } = useChat();
  const mcpStatus = useMCP();
  const { currentTheme, toggleTheme, getAvailableThemes } = useTheme();
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [bottomPopoverOpen, setBottomPopoverOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('chat');
  const [sidebarPanel, setSidebarPanel] = useState<SidebarPanel>('chat');
  const [recentConversations, setRecentConversations] = useState<Conversation[]>([]);
  const [isTabAnimating, setIsTabAnimating] = useState(false);
  const tabContentRef = useRef<HTMLDivElement>(null);

  // 加载最近对话列表
  useEffect(() => {
    getChatHistory(5, 0).then(data => {
      if (data?.items) setRecentConversations(data.items);
    }).catch(() => {});
  }, [activeTab]);

  // 毛玻璃效果状态
  const [glassEffect, setGlassEffect] = useState(() => {
    const saved = localStorage.getItem('glassEffect');
    return saved ? JSON.parse(saved) : false;
  });

  // 打字机效果状态
  const [typewriterEffect, setTypewriterEffect] = useState(() => {
    const saved = localStorage.getItem('typewriterEffect');
    return saved !== null ? JSON.parse(saved) : true;
  });

  // 背景音乐状态
  const [bgMusicEnabled, setBgMusicEnabled] = useState(() => {
    const saved = localStorage.getItem('bgMusicEnabled');
    return saved ? JSON.parse(saved) : false;
  });

  // CRT 效果状态（默认开启）
  const [crtEffect, setCrtEffect] = useState(() => {
    const saved = localStorage.getItem('crtEffect');
    return saved !== null ? JSON.parse(saved) : true;
  });

  // 保存设置到 localStorage
  useEffect(() => {
    localStorage.setItem('glassEffect', JSON.stringify(glassEffect));
    localStorage.setItem('typewriterEffect', JSON.stringify(typewriterEffect));
    localStorage.setItem('bgMusicEnabled', JSON.stringify(bgMusicEnabled));
    localStorage.setItem('crtEffect', JSON.stringify(crtEffect));

    if (glassEffect) {
      document.body.classList.add('glass-effect-enabled');
    } else {
      document.body.classList.remove('glass-effect-enabled');
    }

    if (!crtEffect) {
      document.body.classList.add('crt-disabled');
    } else {
      document.body.classList.remove('crt-disabled');
    }
  }, [glassEffect, typewriterEffect, bgMusicEnabled, crtEffect]);

  // 标签切换（CSS 动画驱动，零 JS DOM 操作）
  const handleTabSwitch = (tabId: TabId) => {
    if (tabId === activeTab || isTabAnimating) return;
    setIsTabAnimating(true);
    setActiveTab(tabId);
    setTimeout(() => setIsTabAnimating(false), 300);
  };

  const handleLoadConversation = (conv: Conversation) => {
    const msgs: Message[] = [];
    if (conv.user_input) {
      msgs.push({
        id: `hist-u-${conv.id}`,
        role: 'user',
        content: conv.user_input,
        timestamp: new Date(conv.created_at).getTime(),
      });
    }
    if (conv.assistant_response) {
      msgs.push({
        id: `hist-a-${conv.id}`,
        role: 'assistant',
        content: conv.assistant_response,
        timestamp: new Date(conv.created_at).getTime() + 1,
        emotion: conv.emotion,
        modelName: conv.model_name,
      });
    }
    if (msgs.length > 0) setMessages(msgs);
    setActiveTab('chat');
    setSidebarPanel('chat');
  };

  return (
    <div className="app-container">
      {/* 背景层 */}
      <AnimatedBackground interval={30000} />

      {/* 背景音乐组件 */}
      <BackgroundMusic
        emotion={messages.length > 1 ? {
          emotion: currentEmotion,
          confidence: 1.0,
          emoji: ''
        } : null}
        enabled={bgMusicEnabled}
        volume={0.3}
      />

      {/* 顶部栏：新建对话 + 用户菜单 */}
      <div className="top-bar">
        <button
          className="top-bar-new-chat"
          onClick={clearMessages}
          title="新建对话"
        >
          +
        </button>
        <UserMenu glassEffect={glassEffect} />
      </div>

      {/* 主布局 */}
      <div className={`main-layout ${glassEffect ? 'glass-effect' : ''}`}>
        {/* ── 左侧面板 ──────────────────────────── */}
        <div className={`left-panel ${glassEffect ? 'glass-effect' : ''}`}>
          {/* ═══ 上部：角色 + ECG ═══ */}
          <div className="left-panel-top">
            <TerminalClock />
            <EmotionIndicator emotion={currentEmotion} glassEffect={glassEffect} />
            <ECGStatusBar
              isActive={!isProcessing}
              emotion={currentEmotion}
              glassEffect={glassEffect}
            />
          </div>

          {/* 分割线 */}
          <div className="left-panel-divider" />

          {/* ═══ 下部：对话 / 交互 双 Tab ═══ */}
          <div className="left-panel-bottom">
            <div className="sidebar-tabs">
              <button
                className={`sidebar-tab ${sidebarPanel === 'chat' ? 'sidebar-tab--active' : ''}`}
                onClick={() => setSidebarPanel('chat')}
              >
                💬 对话
              </button>
              <button
                className={`sidebar-tab ${sidebarPanel === 'interaction' ? 'sidebar-tab--active' : ''}`}
                onClick={() => setSidebarPanel('interaction')}
              >
                🔗 交互
              </button>
            </div>

            {sidebarPanel === 'chat' && (
              <div className="sidebar-recent">
                {recentConversations.length === 0 ? (
                  <p className="sidebar-empty">暂无最近对话</p>
                ) : (
                  <>
                    {recentConversations.map(c => (
                      <button
                        key={c.id}
                        className="sidebar-chat-item"
                        onClick={() => handleLoadConversation(c)}
                      >
                        <span className="sidebar-chat-preview">
                          {c.user_input?.slice(0, 24) || '新对话'}
                        </span>
                        <span className="sidebar-chat-time">
                          {c.created_at ? new Date(c.created_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''}
                        </span>
                      </button>
                    ))}
                    <button
                      className="sidebar-chat-item sidebar-chat-item--all"
                      onClick={() => handleTabSwitch('history')}
                    >
                      <span className="sidebar-chat-preview">查看全部历史 →</span>
                    </button>
                  </>
                )}
              </div>
            )}

            {sidebarPanel === 'interaction' && (
              <div className="sidebar-interaction">
                {INTERACTION_ITEMS.map(item => (
                  <button
                    key={item.id}
                    className={`sidebar-int-item ${activeTab === item.id ? 'sidebar-int-item--active' : ''}`}
                    onClick={() => handleTabSwitch(item.id)}
                  >
                    <span className="sidebar-int-icon">{item.icon}</span>
                    <span className="sidebar-int-label">{item.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 分割线 */}
          <div className="left-panel-divider" />

          {/* ═══ 底部固定栏：用户 popover + 设置 ═══ */}
          <div className="sidebar-bottom">
            <div style={{ position: 'relative', flex: 1 }}>
              <button
                className={`sidebar-bottom-btn ${bottomPopoverOpen ? 'sidebar-bottom-btn--active' : ''}`}
                onClick={() => setBottomPopoverOpen(v => !v)}
                title="用户"
                style={{ width: '100%' }}
              >
                👤
              </button>
              {bottomPopoverOpen && (
                <>
                  <div className="bottom-popover-overlay" onClick={() => setBottomPopoverOpen(false)} />
                  <div className="bottom-popover">
                    <div className="bottom-popover-item" onClick={() => { toggleTheme(currentTheme === 'pixel-dark' ? 'pixel-light' : currentTheme === 'pixel-light' ? 'cyberpunk' : currentTheme === 'cyberpunk' ? 'minimal' : 'pixel-dark'); setBottomPopoverOpen(false); }}>
                      🎨 切换主题
                    </div>
                    <div className="bottom-popover-item" onClick={() => { handleTabSwitch('settings'); setBottomPopoverOpen(false); }}>
                      ⚙ 设置
                    </div>
                    <div className="bottom-popover-divider" />
                    <div className="bottom-popover-item bottom-popover-item--danger" onClick={async () => {
                      setBottomPopoverOpen(false);
                      await authAPI.logout();
                      navigate('/login');
                    }}>
                      🚪 退出
                    </div>
                  </div>
                </>
              )}
            </div>
            <button
              className={`sidebar-bottom-btn ${activeTab === 'settings' ? 'sidebar-bottom-btn--active' : ''}`}
              onClick={() => handleTabSwitch('settings')}
              title="设置"
              style={{ flex: 1 }}
            >
              ⚙
            </button>
          </div>
        </div>

        {/* ── 右侧面板（主内容区）──────────────────── */}
        <div className={`chat-panel ${glassEffect ? 'glass-effect' : ''}`}>
          <div className="tab-content" ref={tabContentRef}>
            {/* Tab 标题栏 */}
            <div className="tab-title-bar">
              <span className="tab-title-text">
                {activeTab === 'chat' && '💬 对话'}
                {activeTab === 'history' && '📜 全部历史'}
                {activeTab === 'settings' && '⚙ 设置'}
                {activeTab === 'dream' && '🌙 梦境'}
                {activeTab === 'starmap' && '✨ 星图'}
                {activeTab === 'showcase' && '🎨 组件'}
                {activeTab === 'humanizer' && '✍️ 人性化'}
              </span>
            </div>

            {activeTab === 'chat' && (
              <>
                <OptimizedMessageList
                  messages={messages}
                  isProcessing={isProcessing}
                  glassEffect={glassEffect}
                  typewriterEffect={typewriterEffect}
                />
                <ChatInput
                  onSend={sendMessage}
                  onRegenerate={() => {
                    const lastUser = [...messages].reverse().find(m => m.role === 'user');
                    if (lastUser) sendMessage(lastUser.content);
                  }}
                  disabled={isProcessing}
                  glassEffect={glassEffect}
                  lastMessage={[...messages].reverse().find(m => m.role === 'user')?.content}
                />
              </>
            )}

            {activeTab === 'history' && (
              <Suspense fallback={<TabFallback />}>
                <HistoryPanel
                  glassEffect={glassEffect}
                  onLoadConversation={handleLoadConversation}
                />
              </Suspense>
            )}

            {activeTab === 'settings' && (
              <SettingsPanel
                glassEffect={glassEffect}
                mcpStatus={mcpStatus}
                typewriterEffect={typewriterEffect}
                setTypewriterEffect={setTypewriterEffect}
                crtEffect={crtEffect}
                setCrtEffect={setCrtEffect}
                bgMusicEnabled={bgMusicEnabled}
                setBgMusicEnabled={setBgMusicEnabled}
                setGlassEffect={setGlassEffect}
                currentTheme={currentTheme}
                onThemeChange={toggleTheme}
                themes={getAvailableThemes()}
              />
            )}

            {activeTab === 'dream' && (
              <Suspense fallback={<TabFallback />}>
                <DreamSpace />
              </Suspense>
            )}

            {activeTab === 'starmap' && (
              <Suspense fallback={<TabFallback />}>
                <StarMapView glassEffect={glassEffect} />
              </Suspense>
            )}

            {activeTab === 'showcase' && (
              <Suspense fallback={<TabFallback />}>
                <div className="settings-panel" style={{ overflowY: 'auto' }}>
                  <ComponentShowcase glassEffect={glassEffect} typewriterEffect={typewriterEffect} />
                </div>
              </Suspense>
            )}

            {activeTab === 'humanizer' && (
              <Suspense fallback={<TabFallback />}>
                <HumanizerPanel />
              </Suspense>
            )}
          </div>
        </div>

        {/* ── 右侧可折叠面板（快捷信息） ──────────── */}
        <div className={`right-panel ${rightPanelOpen ? 'right-panel--open' : 'right-panel--closed'} ${glassEffect ? 'glass-effect' : ''}`}>
          <button
            className="right-panel-toggle"
            onClick={() => setRightPanelOpen(v => !v)}
            title={rightPanelOpen ? '折叠面板' : '展开面板'}
          >
            <span className="right-panel-toggle-icon">
              {rightPanelOpen ? '▶' : '◀'}
            </span>
          </button>

          {!rightPanelOpen && (
            <div className="right-panel-label">
              <span>信</span><span>息</span><span>面</span><span>板</span>
            </div>
          )}

          {rightPanelOpen && (
            <div className="right-panel-content">
              <div className="right-panel-header">
                <span className="pixel-subtitle">📊 快捷信息</span>
              </div>
              <div className="right-panel-body">
                <div className="info-stat">
                  <span className="info-stat-label">消息数</span>
                  <span className="info-stat-value">{messages.length}</span>
                </div>
                <div className="info-stat">
                  <span className="info-stat-label">情绪</span>
                  <span className="info-stat-value">{currentEmotion || '平静'}</span>
                </div>
                <div className="info-stat">
                  <span className="info-stat-label">MCP</span>
                  <span className="info-stat-value" style={{ color: mcpStatus.connected ? 'var(--success)' : 'var(--error)' }}>
                    {mcpStatus.connected ? '● 在线' : '○ 离线'}
                  </span>
                </div>
                <div className="info-stat">
                  <span className="info-stat-label">模型</span>
                  <span className="info-stat-value">自动路由</span>
                </div>
                <div className="info-stat">
                  <span className="info-stat-label">主题</span>
                  <span className="info-stat-value">{currentTheme}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
