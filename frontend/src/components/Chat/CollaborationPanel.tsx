// 陈筱雪 AI 助手 - 协作模式前端集成示例
// 位置: frontend/src/components/Chat/CollaborationPanel.tsx

import React, { useState } from 'react';
import { PixelButton } from '../Common/PixelButton';
import { sendCollaborationChat } from '../../services/api';

interface SubtaskResult {
  type: string;
  model: string;
  content_preview: string;
  confidence: number;
  execution_time_ms: number;
}

interface CollaborationData {
  collaboration_used: boolean;
  subtask_results: SubtaskResult[];
  models_used: string[];
  total_cost: number;
  latency_ms: number;
  reasoning: string;
}

interface CollaborationPanelProps {
  data: CollaborationData | null;
  visible: boolean;
  onClose: () => void;
}

/**
 * 协作详情面板组件
 * 显示多模型协作的执行过程和结果
 */
export const CollaborationPanel: React.FC<CollaborationPanelProps> = ({
  data,
  visible,
  onClose,
}) => {
  const [expandedTask, setExpandedTask] = useState<number | null>(null);

  if (!visible || !data) return null;

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      retrieval: '🔍',
      reasoning: '🧠',
      analysis: '📊',
      synthesis: '📝',
      creation: '✨',
      verification: '✅',
      coding: '💻',
    };
    return icons[type] || '📌';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return '#4ade80'; // 绿色
    if (confidence >= 0.7) return '#fbbf24'; // 黄色
    return '#f87171'; // 红色
  };

  return (
    <div className="collaboration-panel" style={{
      position: 'fixed',
      right: '20px',
      top: '100px',
      width: '400px',
      maxHeight: '600px',
      backgroundColor: 'rgba(30, 30, 46, 0.95)',
      border: '2px solid #6366f1',
      borderRadius: '12px',
      padding: '20px',
      overflowY: 'auto',
      zIndex: 1000,
      boxShadow: '0 8px 32px rgba(99, 102, 241, 0.3)',
    }}>
      {/* 标题栏 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid rgba(99, 102, 241, 0.3)',
      }}>
        <h3 style={{ margin: 0, color: '#6366f1' }}>
          🤝 多模型协作详情
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#fff',
            fontSize: '20px',
            cursor: 'pointer',
          }}
        >
          ×
        </button>
      </div>

      {/* 摘要信息 */}
      <div style={{
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
      }}>
        <div style={{ marginBottom: '8px', color: '#e0e0e0' }}>
          <strong>执行摘要:</strong>
        </div>
        <div style={{ fontSize: '13px', lineHeight: '1.6', whiteSpace: 'pre-line', color: '#b0b0b0' }}>
          {data.reasoning}
        </div>
      </div>

      {/* 子任务列表 */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#e0e0e0',
          marginBottom: '12px',
        }}>
          📋 子任务执行 ({data.subtask_results.length})
        </div>

        {data.subtask_results.map((task, index) => (
          <div
            key={index}
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              borderRadius: '8px',
              marginBottom: '8px',
              overflow: 'hidden',
            }}
          >
            {/* 子任务头部 */}
            <div
              onClick={() => setExpandedTask(expandedTask === index ? null : index)}
              style={{
                padding: '12px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>
                  {getTypeIcon(task.type)}
                </span>
                <div>
                  <div style={{ color: '#e0e0e0', fontSize: '13px', fontWeight: 'bold' }}>
                    {task.type.toUpperCase()}
                  </div>
                  <div style={{ color: '#888', fontSize: '11px' }}>
                    {task.model}
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div
                  style={{
                    color: getConfidenceColor(task.confidence),
                    fontSize: '13px',
                    fontWeight: 'bold',
                  }}
                >
                  {(task.confidence * 100).toFixed(0)}%
                </div>
                <div style={{ color: '#666', fontSize: '11px' }}>
                  {task.execution_time_ms.toFixed(0)}ms
                </div>
              </div>
            </div>

            {/* 展开的内容 */}
            {expandedTask === index && (
              <div
                style={{
                  padding: '12px',
                  borderTop: '1px solid rgba(99, 102, 241, 0.2)',
                  backgroundColor: 'rgba(0, 0, 0, 0.2)',
                }}
              >
                <div style={{
                  fontSize: '12px',
                  color: '#b0b0b0',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                }}>
                  {task.content_preview}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 使用模型列表 */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#e0e0e0',
          marginBottom: '8px',
        }}>
          🤖 参与模型
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {data.models_used.map((model, index) => (
            <span
              key={index}
              style={{
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                color: '#a5b4fc',
                padding: '4px 10px',
                borderRadius: '12px',
                fontSize: '12px',
              }}
            >
              {model}
            </span>
          ))}
        </div>
      </div>

      {/* 成本和性能指标 */}
      <div
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          padding: '12px',
          borderRadius: '8px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
        }}
      >
        <div>
          <div style={{ color: '#888', fontSize: '11px' }}>总耗时</div>
          <div style={{ color: '#e0e0e0', fontSize: '16px', fontWeight: 'bold' }}>
            {(data.latency_ms / 1000).toFixed(2)}s
          </div>
        </div>
        <div>
          <div style={{ color: '#888', fontSize: '11px' }}>总成本</div>
          <div style={{ color: '#4ade80', fontSize: '16px', fontWeight: 'bold' }}>
            ${data.total_cost.toFixed(4)}
          </div>
        </div>
      </div>

      {/* 关闭按钮 */}
      <PixelButton
        onClick={onClose}
        className="pixel-btn--secondary"
        style={{
          width: '100%',
          marginTop: '16px',
        }}
      >
        关闭
      </PixelButton>
    </div>
  );
};

// 在 ChatInput 中添加协作模式开关
export const ChatInputWithCollaboration: React.FC = () => {
  const [message, setMessage] = useState('');
  const [useCollaboration, setUseCollaboration] = useState(false);
  const [collaborationData, setCollaborationData] = useState<CollaborationData | null>(null);
  const [showPanel, setShowPanel] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);

  const handleSend = async () => {
    if (!message.trim()) return;

    try {
      const data = await sendCollaborationChat(
        [{ role: 'user', content: message }],
        useCollaboration,
      ) as CollaborationData & { response: string };

      // 如果使用了协作模式，保存数据并显示面板
      if (data.collaboration_used) {
        setCollaborationData(data);
        setShowPanel(true);
      }

      // 显示消息
      setMessages(prev => [...prev, { role: 'user', content: message }, { role: 'assistant', content: data.response }]);
      setMessage('');
    } catch (error) {
      console.error('发送消息失败:', error);
    }
  };

  return (
    <div>
      {/* 输入框区域 */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="输入消息..."
          style={{
            flex: 1,
            padding: '12px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '8px',
            color: '#fff',
          }}
        />
        <PixelButton onClick={handleSend}>发送</PixelButton>
      </div>

      {/* 协作模式开关 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#b0b0b0',
          fontSize: '13px',
          cursor: 'pointer',
        }}
        onClick={() => setUseCollaboration(!useCollaboration)}
      >
        <input
          type="checkbox"
          checked={useCollaboration}
          onChange={(e) => {
            e.stopPropagation();
            setUseCollaboration(e.target.checked);
          }}
          style={{ cursor: 'pointer' }}
        />
        <span>🤝 启用多模型协作模式(适合复杂问题)</span>
      </div>

      {/* 协作详情面板 */}
      <CollaborationPanel
        data={collaborationData}
        visible={showPanel}
        onClose={() => setShowPanel(false)}
      />
    </div>
  );
};