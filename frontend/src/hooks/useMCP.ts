/**
 * useMCP Hook - MCP 连接状态管理
 */

import { useEffect, useState } from 'react';
import { mcpClient } from '../services/mcpClient';
import { getMCPInfo } from '../services/api';

interface MCPStatus {
  connected: boolean;
  serverName: string;
  serverVersion: string;
  toolsCount: number;
}

export function useMCP(): MCPStatus {
  const [status, setStatus] = useState<MCPStatus>({
    connected: false,
    serverName: '',
    serverVersion: '',
    toolsCount: 0,
  });

  useEffect(() => {
    let mounted = true;

    async function connect() {
      try {
        // 初始化 MCP 客户端
        await mcpClient.initialize();

        // 获取服务器信息
        const info = await getMCPInfo();

        if (mounted) {
          setStatus({
            connected: true,
            serverName: info.name,
            serverVersion: info.version,
            toolsCount: info.tools_count,
          });
        }
      } catch (error) {
        console.warn('[MCP] 连接失败，降级到直接 API 模式:', error);
        if (mounted) {
          setStatus({
            connected: false,
            serverName: '',
            serverVersion: '',
            toolsCount: 0,
          });
        }
      }
    }

    connect();

    return () => {
      mounted = false;
    };
  }, []);

  return status;
}
