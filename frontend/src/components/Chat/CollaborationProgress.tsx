// 协作模式实时进度组件
// 位置: frontend/src/components/Chat/CollaborationProgress.tsx

import React, { useEffect, useState } from 'react';

interface SubtaskStatus {
  id: number;
  type: string;
  model: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number; // 0-100
}

interface CollaborationProgressProps {
  subtasks: SubtaskStatus[];
  visible: boolean;
}

/**
 * 协作任务实时进度条
 * 显示每个子任务的执行状态和进度
 */
export const CollaborationProgress: React.FC<CollaborationProgressProps> = ({
  subtasks,
  visible,
}) => {
  if (!visible || subtasks.length === 0) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'running': return '🔄';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '⚪';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#888';
      case 'running': return '#6366f1';
      case 'completed': return '#4ade80';
      case 'failed': return '#f87171';
      default: return '#666';
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      retrieval: '🔍 检索',
      reasoning: '🧠 推理',
      analysis: '📊 分析',
      synthesis: '📝 总结',
      creation: '✨ 创作',
      verification: '✅ 验证',
      coding: '💻 编码',
    };
    return labels[type] || type;
  };

  return (
    <div style={{
      padding: '16px',
      backgroundColor: 'rgba(30, 30, 46, 0.95)',
      border: '1px solid rgba(99, 102, 241, 0.3)',
      borderRadius: '12px',
      marginBottom: '12px',
    }}>
      <div style={{
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#6366f1',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        <span>🤝</span>
        <span>多模型协作进行中...</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {subtasks.map((task) => (
          <div key={task.id} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 12px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
          }}>
            {/* 状态图标 */}
            <span style={{ fontSize: '18px' }}>
              {getStatusIcon(task.status)}
            </span>

            {/* 任务信息 */}
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '13px',
                color: '#e0e0e0',
                marginBottom: '4px',
              }}>
                {getTypeLabel(task.type)}
              </div>
              <div style={{
                fontSize: '11px',
                color: '#888',
              }}>
                {task.model}
              </div>
            </div>

            {/* 进度条 */}
            {task.status === 'running' && (
              <div style={{
                width: '80px',
                height: '4px',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '2px',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${task.progress}%`,
                  height: '100%',
                  backgroundColor: '#6366f1',
                  transition: 'width 0.3s ease',
                }} />
              </div>
            )}

            {/* 完成状态颜色 */}
            {(task.status === 'completed' || task.status === 'failed') && (
              <span style={{
                fontSize: '12px',
                color: getStatusColor(task.status),
                fontWeight: 'bold',
              }}>
                {task.status === 'completed' ? '完成' : '失败'}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* 总体进度 */}
      <div style={{
        marginTop: '12px',
        paddingTop: '12px',
        borderTop: '1px solid rgba(99, 102, 241, 0.2)',
      }}>
        <div style={{
          fontSize: '12px',
          color: '#b0b0b0',
          marginBottom: '6px',
        }}>
          总体进度: {subtasks.filter(t => t.status === 'completed').length}/{subtasks.length}
        </div>
        <div style={{
          width: '100%',
          height: '6px',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '3px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${(subtasks.filter(t => t.status === 'completed').length / subtasks.length) * 100}%`,
            height: '100%',
            backgroundColor: 'linear-gradient(90deg, #6366f1, #a855f7)',
            background: 'linear-gradient(90deg, #6366f1, #a855f7)',
            transition: 'width 0.3s ease',
          }} />
        </div>
      </div>
    </div>
  );
};