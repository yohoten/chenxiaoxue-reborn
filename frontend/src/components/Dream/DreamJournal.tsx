/**
 * 梦境日记 — 日历视图 + 历史列表 + 统计
 */
import { useState, useEffect } from 'react';
import { getDreamRecords, getDreamMonths, getDreamStats, deleteDreamRecord } from '../../services/api';
import type { DreamRecord, DreamStats } from '../../types';

interface Props {
  onLoadDream: (record: DreamRecord) => void;
  refreshKey: number;
}

export function DreamJournal({ onLoadDream, refreshKey }: Props) {
  const [records, setRecords] = useState<DreamRecord[]>([]);
  const [months, setMonths] = useState<string[]>([]);
  const [stats, setStats] = useState<DreamStats | null>(null);
  const [activeMonth, setActiveMonth] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'list' | 'stats'>('list');

  useEffect(() => {
    loadData();
  }, [activeMonth, refreshKey]);

  async function loadData() {
    setLoading(true);
    try {
      const [recData, monData, statData] = await Promise.all([
        getDreamRecords(50, 0, activeMonth || undefined),
        getDreamMonths(),
        getDreamStats(),
      ]);
      setRecords(recData.items);
      setMonths(monData.months);
      setStats(statData);
    } catch { /* ignore */ }
    setLoading(false);
  }

  async function handleDelete(id: number) {
    if (!confirm('确定删除这条梦境记录吗？')) return;
    try {
      await deleteDreamRecord(id);
      setRecords(prev => prev.filter(r => r.id !== id));
    } catch { /* ignore */ }
  }

  if (loading) {
    return <p style={{ color: '#888', fontSize: 12, textAlign: 'center', padding: 40 }}>加载中...</p>;
  }

  return (
    <div>
      {/* 统计概览 */}
      {stats && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <div style={{ background: 'rgba(58,123,213,0.15)', border: '2px solid #3a7bd5', padding: '10px 16px', textAlign: 'center', flex: 1, minWidth: 80 }}>
            <div style={{ fontSize: 20, fontWeight: 'bold', color: '#3a7bd5' }}>{stats.total_dreams}</div>
            <div style={{ fontSize: 9, color: '#888' }}>总梦境</div>
          </div>
          <div style={{ background: 'rgba(123,58,213,0.15)', border: '2px solid #7b3ad5', padding: '10px 16px', textAlign: 'center', flex: 1, minWidth: 80 }}>
            <div style={{ fontSize: 20, fontWeight: 'bold', color: '#7b3ad5' }}>{stats.monthly_dreams}</div>
            <div style={{ fontSize: 9, color: '#888' }}>本月</div>
          </div>
        </div>
      )}

      {/* 月份筛选 */}
      {months.length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
          <button
            className={`pixel-btn ${!activeMonth ? 'pixel-btn--active' : ''}`}
            onClick={() => setActiveMonth('')}
            style={{ fontSize: 9, padding: '3px 10px', minWidth: 0 }}
          >
            全部
          </button>
          {months.slice(0, 12).map(m => (
            <button
              key={m}
              className={`pixel-btn ${activeMonth === m ? 'pixel-btn--active' : ''}`}
              onClick={() => setActiveMonth(m)}
              style={{ fontSize: 9, padding: '3px 10px', minWidth: 0 }}
            >
              {m}
            </button>
          ))}
        </div>
      )}

      {/* 标签切换 */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
        <button className={`pixel-btn ${tab === 'list' ? 'pixel-btn--active' : ''}`} onClick={() => setTab('list')} style={{ fontSize: 10, padding: '4px 12px', minWidth: 0 }}>
          梦境列表
        </button>
        <button className={`pixel-btn ${tab === 'stats' ? 'pixel-btn--active' : ''}`} onClick={() => setTab('stats')} style={{ fontSize: 10, padding: '4px 12px', minWidth: 0 }}>
          符号统计
        </button>
      </div>

      {tab === 'list' ? (
        records.length === 0 ? (
          <p style={{ color: '#888', fontSize: 11, textAlign: 'center', padding: 30 }}>
            {activeMonth ? '该月份暂无梦境记录' : '还没有梦境记录，去解析你的第一个梦吧 🌙'}
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {records.map(record => (
              <div key={record.id} style={{
                background: 'rgba(7, 8, 17, 0.4)', border: '2px solid #2a3b5a',
                padding: 12, cursor: 'pointer',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                  <span style={{ fontSize: 10, color: '#888' }}>
                    {new Date(record.dream_date).toLocaleDateString('zh-CN')}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      onClick={() => onLoadDream(record)}
                      style={{ fontSize: 9, padding: '2px 8px', border: '1px solid #3a7bd5', background: 'transparent', color: '#3a7bd5', cursor: 'pointer' }}
                    >
                      查看
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(record.id); }}
                      style={{ fontSize: 9, padding: '2px 8px', border: '1px solid #d53a3a', background: 'transparent', color: '#d53a3a', cursor: 'pointer' }}
                    >
                      删除
                    </button>
                  </div>
                </div>
                <p style={{ fontSize: 10, lineHeight: 1.5, color: '#ccc', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {record.dream_text.slice(0, 80)}...
                </p>
                {record.detected_symbols.length > 0 && (
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                    {record.detected_symbols.map((s, i) => (
                      <span key={i} style={{
                        background: 'rgba(58,123,213,0.2)', padding: '1px 6px',
                        fontSize: 9, border: '1px solid #2a3b5a',
                      }}>
                        {s.emoji || ''}{s.symbol}
                      </span>
                    ))}
                  </div>
                )}
                <span style={{ fontSize: 9, color: '#666', marginTop: 4, display: 'block' }}>
                  {record.analysis_type === 'ai_enhanced' ? '🤖 AI增强' : '📖 传统解梦'}
                </span>
              </div>
            ))}
          </div>
        )
      ) : (
        stats && stats.top_symbols.length > 0 ? (
          <div>
            <h4 style={{ fontSize: 11, color: '#888', marginBottom: 8 }}>最常出现的梦境符号</h4>
            {stats.top_symbols.map((item, i) => (
              <div key={item.symbol} style={{
                display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6,
              }}>
                <span style={{ fontSize: 10, color: '#888', width: 24 }}>#{i + 1}</span>
                <span style={{ fontSize: 11, flex: 1 }}>{item.symbol}</span>
                <span style={{
                  background: 'rgba(58,123,213,0.3)', padding: '2px 8px', fontSize: 10, minWidth: 24, textAlign: 'center',
                }}>
                  {item.count}次
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#888', fontSize: 11, textAlign: 'center', padding: 30 }}>暂无符号统计数据</p>
        )
      )}
    </div>
  );
}

export default DreamJournal;
