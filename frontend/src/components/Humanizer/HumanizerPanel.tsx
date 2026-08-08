/**
 * Humanizer Panel - AI 文本检测与人性化改写组件
 * 
 * 功能：
 * 1. 检测文本中的 24 种 AI 写作模式
 * 2. 显示 AI 化程度评分和详细分析
 * 3. 提供一键人性化改写功能
 * 4. 展示改进建议和替换方案
 */

import React, { useState } from 'react';
import { PixelButton } from '../Common/PixelButton';
import { analyzeHumanizer, humanizeText } from '../../services/api';

interface PatternMatch {
  pattern_id: string;
  pattern_name: string;
  severity: 'high' | 'medium' | 'low';
  snippet: string;
  position: number;
  length: number;
  suggestion: string;
  replacement: string;
}

interface HumanizerResult {
  original_text: string;
  humanized_text: string;
  total_issues: number;
  score: number;
  summary: string;
  matches: PatternMatch[];
}

export function HumanizerPanel() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<HumanizerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHumanized, setShowHumanized] = useState(false);

  // 分析文本
  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setError('请输入要分析的文本');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setShowHumanized(false);

    try {
      const data = await analyzeHumanizer(inputText);
      setResult(data as HumanizerResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 人性化改写
  const handleHumanize = async () => {
    if (!inputText.trim()) {
      setError('请输入要改写的文本');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await humanizeText(inputText);
      setResult(data as HumanizerResult);
      setShowHumanized(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '改写失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 获取严重程度颜色
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return '#ff4500';
      case 'medium':
        return '#ffd43b';
      case 'low':
        return '#3aff5e';
      default:
        return '#888';
    }
  };

  // 获取评分颜色
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#ff4500'; // 高 AI 痕迹
    if (score >= 0.4) return '#ffd43b'; // 中等
    return '#3aff5e'; // 低 AI 痕迹
  };

  // 复制文本到剪贴板
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('已复制到剪贴板！');
    });
  };

  return (
    <div className="humanizer-panel" style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      {/* 标题 */}
      <div style={{ marginBottom: '20px', textAlign: 'center' }}>
        <h2 className="pixel-text" style={{ fontSize: '24px', color: '#3aff5e', marginBottom: '8px' }}>
          ✍️ AI 文本人性化检测器
        </h2>
        <p className="pixel-text--secondary" style={{ fontSize: '12px' }}>
          基于 Wikipedia "Signs of AI writing" · 检测 24 种 AI 写作模式
        </p>
      </div>

      {/* 输入区域 - 终端风格 */}
      <div style={{ marginBottom: '20px' }}>
        <label className="pixel-text" style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--success)' }}>
          📝 输入文本（最多 50,000 字符）：
        </label>
        <div className="terminal-grid-bg" style={{ position: 'relative', border: '2px solid #2a3b5a' }}>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="在此粘贴或输入要检测的文本..."
            className="terminal-textarea"
          />
          <span className="terminal-prompt-sign">{'>'}</span>
          {inputText.length > 0 && <span className="terminal-cursor" />}
        </div>
        <div className="terminal-char-count">
          {String(inputText.length).padStart(5, '0')} / 50000
        </div>
      </div>

      {/* 操作按钮 - 终端风格 */}
      <div className="terminal-actions">
        <PixelButton onClick={handleAnalyze} disabled={loading}>
          {'>'} 分析文本
        </PixelButton>
        <PixelButton onClick={handleHumanize} disabled={loading}>
          {'>'} 人性化改写
        </PixelButton>
      </div>

      {/* 错误提示 */}
      {error && (
        <div
          style={{
            padding: '12px',
            background: 'rgba(255, 69, 0, 0.1)',
            border: '2px solid #ff4500',
            borderRadius: '4px',
            marginBottom: '20px',
            color: '#ff4500',
            fontSize: '13px',
          }}
        >
          ❌ {error}
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div className="loading-indicator">⏳ 正在分析中...</div>
        </div>
      )}

      {/* 分析结果 */}
      {result && !loading && (
        <div>
          {/* 评分卡片 */}
          <div
            style={{
              padding: '16px',
              background: 'rgba(7, 8, 17, 0.8)',
              border: '3px solid #2a3b5a',
              borderRadius: '4px',
              marginBottom: '20px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.score), marginBottom: '8px' }}>
              {(result.score * 100).toFixed(0)}%
            </div>
            <div className="pixel-text" style={{ fontSize: '16px', marginBottom: '4px' }}>
              AI 化程度评分
            </div>
            <div className="pixel-text--secondary" style={{ fontSize: '12px' }}>
              检测到 {result.total_issues} 处问题
            </div>
            <div style={{ marginTop: '8px', fontSize: '13px', color: getScoreColor(result.score) }}>
              {result.score >= 0.7 ? '🔴 高 AI 痕迹' : result.score >= 0.4 ? '🟡 中等' : '🟢 低 AI 痕迹'}
            </div>
          </div>

          {/* 分析摘要 */}
          {result.summary && (
            <div
              style={{
                padding: '12px',
                background: 'rgba(58, 255, 94, 0.05)',
                border: '2px solid #3aff5e',
                borderRadius: '4px',
                marginBottom: '20px',
                fontSize: '13px',
                lineHeight: '1.6',
              }}
            >
              <strong style={{ color: '#3aff5e' }}>📊 分析摘要：</strong>
              <div style={{ marginTop: '8px' }}>{result.summary}</div>
            </div>
          )}

          {/* 原文 vs 人性化版本切换 */}
          {result.humanized_text && result.humanized_text !== result.original_text && (
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <button
                  onClick={() => setShowHumanized(false)}
                  style={{
                    padding: '8px 16px',
                    background: !showHumanized ? '#3aff5e' : 'transparent',
                    color: !showHumanized ? '#000' : '#3aff5e',
                    border: '2px solid #3aff5e',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 'bold',
                  }}
                >
                  📄 原文
                </button>
                <button
                  onClick={() => setShowHumanized(true)}
                  style={{
                    padding: '8px 16px',
                    background: showHumanized ? '#3aff5e' : 'transparent',
                    color: showHumanized ? '#000' : '#3aff5e',
                    border: '2px solid #3aff5e',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 'bold',
                  }}
                >
                  ✨ 人性化版本
                </button>
                <button
                  onClick={() => copyToClipboard(showHumanized ? result.humanized_text : result.original_text)}
                  style={{
                    padding: '8px 16px',
                    background: 'transparent',
                    color: '#ffd43b',
                    border: '2px solid #ffd43b',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    marginLeft: 'auto',
                  }}
                >
                  📋 复制
                </button>
              </div>

              <div
                style={{
                  padding: '12px',
                  background: 'rgba(7, 8, 17, 0.8)',
                  border: '3px solid #2a3b5a',
                  borderRadius: '4px',
                  fontSize: '13px',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {showHumanized ? result.humanized_text : result.original_text}
              </div>
            </div>
          )}

          {/* 详细匹配列表 */}
          {result.matches.length > 0 && (
            <div>
              <h3 className="pixel-text" style={{ fontSize: '16px', marginBottom: '12px', color: '#3aff5e' }}>
                🔎 检测到的 AI 写作模式（{result.matches.length} 处）
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {result.matches.map((match, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '12px',
                      background: 'rgba(7, 8, 17, 0.8)',
                      border: `2px solid ${getSeverityColor(match.severity)}`,
                      borderRadius: '4px',
                    }}
                  >
                    {/* 模式头部 */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span
                        style={{
                          padding: '4px 8px',
                          background: getSeverityColor(match.severity),
                          color: '#000',
                          borderRadius: '2px',
                          fontSize: '11px',
                          fontWeight: 'bold',
                        }}
                      >
                        {match.pattern_id}
                      </span>
                      <span className="pixel-text" style={{ fontSize: '14px', fontWeight: 'bold' }}>
                        {match.pattern_name}
                      </span>
                      <span
                        style={{
                          marginLeft: 'auto',
                          padding: '2px 6px',
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderRadius: '2px',
                          fontSize: '10px',
                          textTransform: 'uppercase',
                        }}
                      >
                        {match.severity}
                      </span>
                    </div>

                    {/* 匹配片段 */}
                    <div
                      style={{
                        padding: '8px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: '2px',
                        marginBottom: '8px',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        color: '#ffd43b',
                      }}
                    >
                      "{match.snippet}"
                    </div>

                    {/* 建议 */}
                    <div style={{ fontSize: '12px', lineHeight: '1.5' }}>
                      <strong style={{ color: '#3aff5e' }}>💡 建议：</strong>
                      <span style={{ marginLeft: '4px' }}>{match.suggestion}</span>
                    </div>

                    {/* 替换文本（如果有） */}
                    {match.replacement && (
                      <div style={{ marginTop: '8px', fontSize: '12px' }}>
                        <strong style={{ color: '#4ecdc4' }}>🔄 替换为：</strong>
                        <code
                          style={{
                            marginLeft: '4px',
                            padding: '2px 6px',
                            background: 'rgba(78, 205, 196, 0.1)',
                            borderRadius: '2px',
                          }}
                        >
                          {match.replacement}
                        </code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 无问题提示 */}
          {result.matches.length === 0 && (
            <div
              style={{
                padding: '20px',
                textAlign: 'center',
                background: 'rgba(58, 255, 94, 0.05)',
                border: '2px solid #3aff5e',
                borderRadius: '4px',
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>✅</div>
              <div className="pixel-text" style={{ fontSize: '16px', color: '#3aff5e' }}>
                太棒了！未检测到 AI 写作模式
              </div>
              <div className="pixel-text--secondary" style={{ fontSize: '12px', marginTop: '8px' }}>
                这段文本看起来非常自然和人性化
              </div>
            </div>
          )}
        </div>
      )}

      {/* 使用说明 */}
      {!result && !loading && (
        <div
          style={{
            padding: '16px',
            background: 'rgba(7, 8, 17, 0.6)',
            border: '2px dashed #2a3b5a',
            borderRadius: '4px',
            fontSize: '12px',
            lineHeight: '1.8',
          }}
        >
          <h4 className="pixel-text" style={{ fontSize: '14px', marginBottom: '12px', color: '#3aff5e' }}>
            📖 使用说明
          </h4>
          <ul style={{ paddingLeft: '20px', margin: 0 }}>
            <li><strong>🔍 分析文本</strong>：检测文本中的 24 种 AI 写作模式，返回详细报告</li>
            <li><strong>✨ 人性化改写</strong>：自动修复检测到的问题，生成更自然的文本</li>
            <li><strong>评分系统</strong>：0% = 完全人类，100% = 完全 AI 化</li>
            <li><strong>严重程度</strong>：High（严重）、Medium（中等）、Low（轻微）</li>
          </ul>
          <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #2a3b5a' }}>
            <strong>支持的检测模式：</strong>P1-P24（内容、语言、风格、沟通、填充五大类）
          </div>
        </div>
      )}
    </div>
  );
}
