// 智能模型选择器组件
// 位置: frontend/src/components/Chat/ModelSelector.tsx

import React, { useState } from 'react';
import { PixelButton } from '../Common/PixelButton';

interface ModelInfo {
  provider: string;
  model: string;
  cost_per_1k: number;
  capabilities: string[];
  priority: number;
  latency_ms: number;
}

interface ModelSelectorProps {
  models: ModelInfo[];
  selectedModel: string | null;
  onModelSelect: (model: string | null) => void;
  useAutoRouting: boolean;
  onAutoRoutingToggle: (enabled: boolean) => void;
}

/**
 * 智能模型选择器
 * 支持自动路由和手动选择两种模式
 */
export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModel,
  onModelSelect,
  useAutoRouting,
  onAutoRoutingToggle,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      deepseek: '🚀',
      openai: '🤖',
      qwen: '🐉',
      doubao: '🎯',
      kimi: '🌙',
      claude: '🧠',
    };
    return icons[provider] || '📦';
  };

  const getCapabilityBadges = (capabilities: string[]) => {
    const badges: Record<string, { icon: string; label: string }> = {
      chat: { icon: '💬', label: '对话' },
      code: { icon: '💻', label: '代码' },
      reasoning: { icon: '🧠', label: '推理' },
      vision: { icon: '👁️', label: '视觉' },
      long_context: { icon: '📚', label: '长文本' },
    };

    return capabilities.slice(0, 3).map(cap => {
      const badge = badges[cap];
      return badge ? (
        <span
          key={cap}
          style={{
            fontSize: '10px',
            padding: '2px 6px',
            backgroundColor: 'rgba(99, 102, 241, 0.2)',
            color: '#a5b4fc',
            borderRadius: '4px',
            marginRight: '4px',
          }}
        >
          {badge.icon} {badge.label}
        </span>
      ) : null;
    });
  };

  return (
    <div style={{
      padding: '12px',
      backgroundColor: 'rgba(30, 30, 46, 0.8)',
      border: '1px solid rgba(99, 102, 241, 0.2)',
      borderRadius: '8px',
      marginBottom: '12px',
    }}>
      {/* 自动路由开关 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px',
      }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#e0e0e0',
          fontSize: '13px',
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={useAutoRouting}
            onChange={(e) => onAutoRoutingToggle(e.target.checked)}
            style={{ cursor: 'pointer' }}
          />
          <span>🎯 智能路由（推荐）</span>
        </label>

        {!useAutoRouting && (
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: 'none',
              border: 'none',
              color: '#6366f1',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            {showAdvanced ? '收起 ▲' : '展开 ▼'}
          </button>
        )}
      </div>

      {/* 手动选择模式 */}
      {!useAutoRouting && showAdvanced && (
        <div style={{
          maxHeight: '300px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}>
          {/* 自动选项 */}
          <div
            onClick={() => onModelSelect(null)}
            style={{
              padding: '10px 12px',
              backgroundColor: selectedModel === null ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: selectedModel === null ? '1px solid #6366f1' : '1px solid transparent',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div>
                <div style={{ color: '#e0e0e0', fontSize: '13px', fontWeight: 'bold' }}>
                  ⚡ 自动选择
                </div>
                <div style={{ color: '#888', fontSize: '11px', marginTop: '4px' }}>
                  根据任务类型智能选择最佳模型
                </div>
              </div>
              {selectedModel === null && (
                <span style={{ color: '#4ade80', fontSize: '16px' }}>✓</span>
              )}
            </div>
          </div>

          {/* 模型列表 */}
          {models.map((model) => (
            <div
              key={`${model.provider}/${model.model}`}
              onClick={() => onModelSelect(`${model.provider}/${model.model}`)}
              style={{
                padding: '10px 12px',
                backgroundColor: selectedModel === `${model.provider}/${model.model}` ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                border: selectedModel === `${model.provider}/${model.model}` ? '1px solid #6366f1' : '1px solid transparent',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '6px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '16px' }}>
                    {getProviderIcon(model.provider)}
                  </span>
                  <div>
                    <div style={{ color: '#e0e0e0', fontSize: '13px', fontWeight: 'bold' }}>
                      {model.model}
                    </div>
                    <div style={{ color: '#888', fontSize: '11px' }}>
                      {model.provider}
                    </div>
                  </div>
                </div>
                {selectedModel === `${model.provider}/${model.model}` && (
                  <span style={{ color: '#4ade80', fontSize: '16px' }}>✓</span>
                )}
              </div>

              {/* 能力和成本信息 */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginTop: '6px',
              }}>
                <div>{getCapabilityBadges(model.capabilities)}</div>
                <div style={{
                  fontSize: '11px',
                  color: model.cost_per_1k < 0.05 ? '#4ade80' : '#fbbf24',
                }}>
                  ${model.cost_per_1k}/1k tokens
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 当前选择提示 */}
      {useAutoRouting && (
        <div style={{
          fontSize: '12px',
          color: '#888',
          textAlign: 'center',
          padding: '8px',
        }}>
          ✨ 系统将根据任务复杂度自动选择最优模型
        </div>
      )}
    </div>
  );
};