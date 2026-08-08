/**
 * 快速操作栏组件 - 增强像素风格
 * 提供常用功能的快捷按钮
 */

interface QuickActionBarProps {
  onClearMessages?: () => void;
  onExportChat?: () => void;
  onToggleTheme?: () => void;
  glassEffect?: boolean;
}

export function QuickActionBar({
  onClearMessages,
  onExportChat,
  onToggleTheme,
  glassEffect = false,
}: QuickActionBarProps) {
  return (
    <div className={`quick-action-bar ${glassEffect ? 'glass-effect' : ''}`}>
      <button
        className="pixel-btn"
        onClick={onExportChat}
        type="button"
        style={{ flex: 1, fontSize: 11 }}
        title="导出对话"
      >
        📤 导出
      </button>
      
      <button
        className="pixel-btn"
        onClick={onToggleTheme}
        type="button"
        style={{ flex: 1, fontSize: 11 }}
        title="切换主题"
      >
        🎨 主题
      </button>
      
      <button
        className="pixel-btn pixel-btn--danger"
        onClick={() => {
          if (window.confirm('确定要清空所有消息吗？此操作不可撤销。')) {
            onClearMessages?.();
          }
        }}
        type="button"
        style={{ flex: 1, fontSize: 11 }}
        title="清空消息"
      >
        🗑️ 清空
      </button>
    </div>
  );
}
