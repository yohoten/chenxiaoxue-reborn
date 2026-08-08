/**
 * UI 组件展示页面
 * 用于预览和测试所有像素风格组件
 */

import { PixelButton } from '../Common/PixelButton';
import { QuickActionBar } from '../Common/QuickActionBar';
import { ChatBubble } from '../Chat/ChatBubble';
import { CharacterPanel } from '../Emotion/CharacterPanel';
import { ECGStatusBar } from '../Emotion/ECGStatusBar';
import type { Message } from '../../types';

interface ComponentShowcaseProps {
  glassEffect?: boolean;
  typewriterEffect?: boolean;
}

export function ComponentShowcase({ glassEffect = false, typewriterEffect = false }: ComponentShowcaseProps) {
  const sampleMessages: Message[] = [
    {
      id: '1',
      role: 'user',
      content: '你好，陈筱雪！',
      timestamp: Date.now(),
    },
    {
      id: '2',
      role: 'assistant',
      content: '你好呀！很高兴见到你 😊\n今天过得怎么样？',
      timestamp: Date.now() + 1000,
      modelName: 'DeepSeek',
    },
  ];

  return (
    <div style={{ padding: 20, maxWidth: 800, margin: '0 auto' }}>
      <h1 className="pixel-title">🎨 UI 组件展示</h1>

      {/* 按钮展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">按钮组件</h2>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <PixelButton variant="default">默认按钮</PixelButton>
          <PixelButton variant="primary">主要按钮</PixelButton>
          <PixelButton variant="danger">危险按钮</PixelButton>
          <PixelButton variant="secondary">次要按钮</PixelButton>
          <PixelButton variant="nav" active>导航激活</PixelButton>
          <PixelButton variant="nav">导航未激活</PixelButton>
          <PixelButton disabled>禁用按钮</PixelButton>
        </div>
      </section>

      {/* 角色面板展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">角色面板</h2>
        <div style={{ width: 300, height: 350 }}>
          <CharacterPanel emotion="happy" />
        </div>
      </section>

      {/* ECG 状态栏展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">ECG 状态栏</h2>
        <ECGStatusBar isActive={true} />
      </section>

      {/* 聊天气泡展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">聊天气泡</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {sampleMessages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} glassEffect={glassEffect} typewriterEffect={typewriterEffect} />
          ))}
        </div>
      </section>

      {/* 快速操作栏展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">快速操作栏</h2>
        <QuickActionBar
          onClearMessages={() => alert('清空消息')}
          onExportChat={() => alert('导出聊天')}
          onToggleTheme={() => alert('切换主题')}
          glassEffect={glassEffect}
        />
      </section>

      {/* 颜色系统展示 */}
      <section style={{ marginBottom: 30 }}>
        <h2 className="pixel-subtitle">颜色系统</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
          <div style={{ background: '#1a1a2e', padding: 20, textAlign: 'center', border: '2px solid #fff' }}>
            <div>#1a1a2e</div>
            <div style={{ fontSize: 12 }}>背景色</div>
          </div>
          <div style={{ background: '#ff9d00', padding: 20, textAlign: 'center' }}>
            <div>#ff9d00</div>
            <div style={{ fontSize: 12 }}>高亮色</div>
          </div>
          <div style={{ background: '#3aff5e', padding: 20, textAlign: 'center' }}>
            <div>#3aff5e</div>
            <div style={{ fontSize: 12 }}>成功色</div>
          </div>
          <div style={{ background: '#4a77c5', padding: 20, textAlign: 'center' }}>
            <div>#4a77c5</div>
            <div style={{ fontSize: 12 }}>强调色</div>
          </div>
        </div>
      </section>
    </div>
  );
}
