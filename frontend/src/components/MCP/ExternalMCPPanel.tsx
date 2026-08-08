/**
 * 外部 MCP 服务器管理面板
 */

import React, { useState, useEffect } from 'react';
import { getExternalMCPServers } from '../../services/api';

interface MCPServer {
  type: string;
  url: string;
  enabled: boolean;
  tools_count: number;
  connected: boolean;
}

interface ExternalServersInfo {
  servers: Record<string, MCPServer>;
  total: number;
}

export const ExternalMCPPanel: React.FC = () => {
  const [servers, setServers] = useState<ExternalServersInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServers = async () => {
    try {
      setLoading(true);
      const data = await getExternalMCPServers() as ExternalServersInfo;
      setServers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  if (loading) {
    return (
      <div className="external-mcp-panel">
        <h2>🔌 外部 MCP 服务器</h2>
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="external-mcp-panel">
        <h2>🔌 外部 MCP 服务器</h2>
        <div className="error">❌ {error}</div>
        <button onClick={fetchServers}>重试</button>
      </div>
    );
  }

  if (!servers || servers.total === 0) {
    return (
      <div className="external-mcp-panel">
        <h2>🔌 外部 MCP 服务器</h2>
        <div className="empty">
          <p>暂无配置的外部服务器</p>
          <p className="hint">
            在 <code>backend/config/mcp_servers.json</code> 中添加配置
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="external-mcp-panel">
      <h2>🔌 外部 MCP 服务器</h2>
      <div className="server-list">
        {Object.entries(servers.servers).map(([name, server]) => (
          <div key={name} className={`server-card ${server.enabled ? 'enabled' : 'disabled'}`}>
            <div className="server-header">
              <h3>{name}</h3>
              <span className={`status-badge ${server.connected ? 'connected' : 'disconnected'}`}>
                {server.connected ? '● 已连接' : '○ 未连接'}
              </span>
            </div>
            
            <div className="server-info">
              <div className="info-row">
                <span className="label">类型:</span>
                <span className="value">{server.type.toUpperCase()}</span>
              </div>
              <div className="info-row">
                <span className="label">URL:</span>
                <span className="value url">{server.url}</span>
              </div>
              <div className="info-row">
                <span className="label">状态:</span>
                <span className="value">
                  {server.enabled ? '✓ 启用' : '✗ 禁用'}
                </span>
              </div>
              <div className="info-row">
                <span className="label">工具数量:</span>
                <span className="value">{server.tools_count}</span>
              </div>
            </div>
            
            {!server.enabled && (
              <div className="disabled-hint">
                此服务器已禁用，请在配置文件中启用
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="panel-footer">
        <button onClick={fetchServers} className="refresh-btn">
          🔄 刷新
        </button>
        <p className="hint">
          配置文件: backend/config/mcp_servers.json
        </p>
      </div>
    </div>
  );
};