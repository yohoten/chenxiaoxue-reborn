/**
 * 历史对话面板组件
 * 显示、管理和加载历史对话记录
 */

import { useEffect, useState } from 'react';
import { getChatHistory, deleteChatHistory } from '../../services/api';
import { PixelButton } from '../Common/PixelButton';
import type { Conversation } from '../../types';

interface HistoryPanelProps {
  glassEffect?: boolean;
  onLoadConversation?: (conversation: Conversation) => void;
}

type TimeFilter = 'all' | 'today' | 'week' | 'month' | '3months';
type SortOption = 'newest' | 'oldest' | 'longest' | 'shortest';

export function HistoryPanel({ glassEffect = false, onLoadConversation }: HistoryPanelProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [viewingConversation, setViewingConversation] = useState<Conversation | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all');
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [showFilters, setShowFilters] = useState(false);
  const [favoritedIds, setFavoritedIds] = useState<number[]>(() => {
    const saved = localStorage.getItem('favoritedConversations');
    return saved ? JSON.parse(saved) : [];
  });
  const pageSize = 20;

  // 保存收藏状态到 localStorage
  useEffect(() => {
    localStorage.setItem('favoritedConversations', JSON.stringify(favoritedIds));
  }, [favoritedIds]);

  // 加载历史对话
  const loadHistory = async () => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * pageSize;
      const data = await getChatHistory(pageSize, offset);
      setConversations(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('加载历史对话失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [currentPage]);

  // 删除单条对话
  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这条对话记录吗？')) return;
    
    try {
      await deleteChatHistory(id);
      // 重新加载列表
      loadHistory();
      // 从选中列表中移除
      setSelectedIds(prev => prev.filter(sid => sid !== id));
      // 从收藏列表中移除
      setFavoritedIds(prev => prev.filter(fid => fid !== id));
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败，请重试');
    }
  };

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) return;
    if (!confirm(`确定要删除选中的 ${selectedIds.length} 条对话记录吗？`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => deleteChatHistory(id)));
      setSelectedIds([]);
      setFavoritedIds(prev => prev.filter(id => !selectedIds.includes(id)));
      loadHistory();
    } catch (error) {
      console.error('批量删除失败:', error);
      alert('批量删除失败，请重试');
    }
  };

  // 切换选择状态
  const toggleSelect = (id: number) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(sid => sid !== id) : [...prev, id]
    );
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedIds.length === conversations.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(conversations.map(conv => conv.id));
    }
  };

  // 切换收藏状态
  const toggleFavorite = (id: number) => {
    setFavoritedIds(prev => 
      prev.includes(id) ? prev.filter(fid => fid !== id) : [...prev, id]
    );
  };

  // 导出选中的对话
  const handleExport = () => {
    const toExport = selectedIds.length > 0 
      ? conversations.filter(conv => selectedIds.includes(conv.id))
      : conversations;
    
    const dataStr = JSON.stringify(toExport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // 加载对话到当前聊天
  const handleLoad = (conv: Conversation) => {
    if (onLoadConversation) {
      onLoadConversation(conv);
    }
  };

  // 格式化时间 - 复古终端风格
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // 小于1分钟
    if (diff < 60000) {
      return "[1m]";
    }
    // 小于1小时
    if (diff < 3600000) {
      return `[${Math.floor(diff / 60000)}m]`;
    }
    // 小于24小时
    if (diff < 86400000) {
      return `[${Math.floor(diff / 3600000)}h]`;
    }
    // 小于7天
    if (diff < 604800000) {
      return `[${Math.floor(diff / 86400000)}d]`;
    }
    // 大于7天
    return `[${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}]`;
  };

  // 获取完整日期字符串
  const getFullDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 时间过滤函数
  const filterByTime = (convs: Conversation[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (timeFilter) {
      case 'today':
        return convs.filter(conv => new Date(conv.created_at) >= today);
      case 'week':
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        return convs.filter(conv => new Date(conv.created_at) >= weekAgo);
      case 'month':
        const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        return convs.filter(conv => new Date(conv.created_at) >= monthAgo);
      case '3months':
        const threeMonthsAgo = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        return convs.filter(conv => new Date(conv.created_at) >= threeMonthsAgo);
      default:
        return convs;
    }
  };

  // 排序函数
  const sortByOption = (convs: Conversation[]) => {
    const sorted = [...convs];
    switch (sortBy) {
      case 'newest':
        return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      case 'oldest':
        return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case 'longest':
        return sorted.sort((a, b) => {
          const lenA = (a.user_input.length + (a.assistant_response?.length || 0));
          const lenB = (b.user_input.length + (b.assistant_response?.length || 0));
          return lenB - lenA;
        });
      case 'shortest':
        return sorted.sort((a, b) => {
          const lenA = (a.user_input.length + (a.assistant_response?.length || 0));
          const lenB = (b.user_input.length + (b.assistant_response?.length || 0));
          return lenA - lenB;
        });
      default:
        return sorted;
    }
  };

  // 过滤搜索结果
  const filteredConversations = sortByOption(
    filterByTime(
      searchQuery.trim() 
        ? conversations.filter(conv => 
            conv.user_input.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (conv.assistant_response && conv.assistant_response.toLowerCase().includes(searchQuery.toLowerCase()))
          )
        : conversations
    )
  );

  const totalPages = Math.ceil(total / pageSize);

  // 查看对话详情
  if (viewingConversation) {
    return (
      <div className={`history-panel ${glassEffect ? 'glass-effect' : ''}`}>
        <div className="history-detail-header">
          <PixelButton onClick={() => setViewingConversation(null)}>
            ← 返回列表
          </PixelButton>
          <div className="history-detail-actions">
            <button
              className={`favorite-btn ${favoritedIds.includes(viewingConversation.id) ? 'active' : ''}`}
              onClick={() => toggleFavorite(viewingConversation.id)}
              title={favoritedIds.includes(viewingConversation.id) ? '取消收藏' : '收藏'}
            >
              {favoritedIds.includes(viewingConversation.id) ? '⭐' : '☆'}
            </button>
            <span className="history-detail-time">
              {getFullDate(viewingConversation.created_at)}
            </span>
          </div>
        </div>
        
        <div className="history-detail-content">
          <div className="history-detail-user">
            <div className="detail-label">👤 用户</div>
            <div className="detail-text">{viewingConversation.user_input}</div>
          </div>
          
          <div className="history-detail-ai">
            <div className="detail-label">🤖 陈筱雪</div>
            <div className="detail-text">{viewingConversation.assistant_response}</div>
          </div>
          
          <div className="history-detail-meta">
            {viewingConversation.model_name && (
              <span className="meta-item">模型: {viewingConversation.model_name}</span>
            )}
            {viewingConversation.emotion && (
              <span className="meta-item">情感: {viewingConversation.emotion}</span>
            )}
            <span className="meta-item">
              长度: {viewingConversation.user_input.length + (viewingConversation.assistant_response?.length || 0)} 字符
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`history-panel ${glassEffect ? 'glass-effect' : ''}`}>
      <div className="history-header">
        <h3 className="pixel-subtitle">📜 历史对话</h3>
        <span className="history-count">{total} 条记录</span>
      </div>

      {/* 搜索栏 */}
      <div className="history-search-bar">
        <input
          type="text"
          className="history-search-input"
          placeholder="🔍 搜索对话内容..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <PixelButton 
          onClick={() => setShowFilters(!showFilters)}
          variant="secondary"
          className="filter-toggle-btn"
        >
          {showFilters ? '隐藏筛选' : '高级筛选'}
        </PixelButton>
      </div>

      {/* 高级筛选面板 */}
      {showFilters && (
        <div className="history-filters">
          <div className="filter-group">
            <label>时间范围:</label>
            <select 
              value={timeFilter} 
              onChange={(e) => setTimeFilter(e.target.value as TimeFilter)}
              className="filter-select"
            >
              <option value="all">全部时间</option>
              <option value="today">今天</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="3months">最近3个月</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>排序方式:</label>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="filter-select"
            >
              <option value="newest">最新优先</option>
              <option value="oldest">最早优先</option>
              <option value="longest">最长对话</option>
              <option value="shortest">最短对话</option>
            </select>
          </div>

          <div className="filter-actions">
            <PixelButton onClick={handleExport} variant="secondary">
              📥 导出数据
            </PixelButton>
            <PixelButton onClick={() => {
              setTimeFilter('all');
              setSortBy('newest');
              setSearchQuery('');
            }}>
              重置筛选
            </PixelButton>
          </div>
        </div>
      )}

      {/* 批量操作栏 */}
      {selectedIds.length > 0 && (
        <div className="history-batch-actions">
          <span className="batch-info">已选择 {selectedIds.length} 条</span>
          <PixelButton onClick={handleBatchDelete} variant="secondary">
            🗑️ 批量删除
          </PixelButton>
          <PixelButton onClick={handleExport}>
            📥 导出选中
          </PixelButton>
          <PixelButton onClick={() => setSelectedIds([])}>
            取消选择
          </PixelButton>
        </div>
      )}

      {loading ? (
        <div className="history-loading">
          <div className="pixel-text">加载中...</div>
        </div>
      ) : filteredConversations.length === 0 ? (
        <div className="history-empty">
          <div className="empty-icon">📭</div>
          <div className="pixel-text--secondary">
            {searchQuery || timeFilter !== 'all' ? '未找到匹配的对话' : '暂无历史对话'}
          </div>
        </div>
      ) : (
        <>
          <div className="history-list">
            {filteredConversations.map((conv) => (
              <div 
                key={conv.id} 
                className={`history-item ${selectedIds.includes(conv.id) ? 'selected' : ''} ${favoritedIds.includes(conv.id) ? 'favorited' : ''}`}
              >
                {/* 选择框 */}
                <input
                  type="checkbox"
                  className="history-checkbox"
                  checked={selectedIds.includes(conv.id)}
                  onChange={() => toggleSelect(conv.id)}
                  onClick={(e) => e.stopPropagation()}
                />
                
                <div
                  className="history-item-content"
                  onClick={() => setViewingConversation(conv)}
                >
                  <div className="history-item-header">
                    <span className="history-time--retro">{formatTime(conv.created_at)}</span>
                    {favoritedIds.includes(conv.id) && (
                      <span className="favorite-badge">⭐</span>
                    )}
                  </div>
                  <div className="history-item-preview">
                    <span className="user-text">💬 {conv.user_input.substring(0, 50)}{conv.user_input.length > 50 ? '...' : ''}</span>
                  </div>
                  <div className="history-item-meta">
                    <span className="history-model">{conv.model_name || 'AI'}</span>
                    <span className="meta-divider">|</span>
                    {conv.emotion && (
                      <>
                        <span className="history-emotion">{conv.emotion}</span>
                        <span className="meta-divider">|</span>
                      </>
                    )}
                    <span className="history-length">
                      {conv.user_input.length + (conv.assistant_response?.length || 0)}c
                    </span>
                  </div>
                </div>
                
                <div className="history-item-actions">
                  <button
                    className={`favorite-btn ${favoritedIds.includes(conv.id) ? 'active' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(conv.id);
                    }}
                    title={favoritedIds.includes(conv.id) ? '取消收藏' : '收藏'}
                  >
                    {favoritedIds.includes(conv.id) ? '⭐' : '☆'}
                  </button>
                  <button
                    className="history-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(conv.id);
                    }}
                    title="删除"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* 分页控制 */}
          {totalPages > 1 && (
            <div className="history-pagination">
              <PixelButton
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                ◀ 上一页
              </PixelButton>
              
              <span className="pagination-info">
                {currentPage} / {totalPages}
              </span>
              
              <PixelButton
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                下一页 ▶
              </PixelButton>
            </div>
          )}
        </>
      )}
    </div>
  );
}
