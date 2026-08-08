/**
 * 聊天输入组件 — auto-resize textarea / 重新生成 / 语音预留
 */
import { useRef, useState, useEffect, useCallback } from 'react';

interface ChatInputProps {
  onSend: (text: string) => void;
  onRegenerate?: () => void;
  disabled: boolean;
  glassEffect?: boolean;
  lastMessage?: string;
}

export function ChatInput({ onSend, onRegenerate, disabled, glassEffect = false, lastMessage }: ChatInputProps) {
  const taRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  const handleSend = useCallback(() => {
    const ta = taRef.current;
    if (!ta || !ta.value.trim() || disabled) return;
    onSend(ta.value.trim());
    ta.value = '';
    ta.style.height = 'auto';
    ta.focus();
  }, [onSend, disabled]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.ctrlKey && e.key === '`') {
      e.preventDefault();
    }
  };

  const autoResize = () => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
  };

  useEffect(() => { autoResize(); }, []);

  return (
    <div className={`input-area ${glassEffect ? 'glass-effect' : ''}`}>
      <div className="input-area-inner">
        <span className={`input-prompt ${isFocused ? 'input-prompt--active' : ''}`}>
          {'>'}
        </span>
        <textarea
          ref={taRef}
          className={`chat-textarea ${glassEffect ? 'glass-effect' : ''}`}
          placeholder={isFocused ? '输入消息… Ctrl+Enter 发送' : '输入消息…'}
          onKeyDown={handleKeyDown}
          onInput={autoResize}
          disabled={disabled}
          autoFocus
          rows={2}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        <div className="input-tools">
          {onRegenerate && lastMessage && (
            <button className="input-tool-btn" title="重新生成回复" onClick={onRegenerate} disabled={disabled} type="button">
              🔄
            </button>
          )}
          <button className="input-tool-btn" title="语音输入 (Ctrl+`)" onClick={() => {}} type="button">
            🎤
          </button>
          <span className="input-hint" title="回车发送，Shift+Enter 换行">
            ↵
          </span>
        </div>
      </div>
    </div>
  );
}
