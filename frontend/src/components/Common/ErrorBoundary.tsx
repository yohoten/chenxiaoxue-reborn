/**
 * ErrorBoundary 错误边界组件
 * 
 * 防止单个组件崩溃导致整个应用白屏，提供友好的错误恢复界面
 */

import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ErrorBoundary] 捕获到组件错误:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // 自定义回退 UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          background: '#1a1a2e',
          color: '#e0e0e0',
          fontFamily: '"Press Start 2P", monospace',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>💥</div>
          <h2 style={{ fontSize: '16px', marginBottom: '12px', color: '#ff6b6b' }}>
            出了点问题
          </h2>
          <p style={{ fontSize: '11px', color: '#888', marginBottom: '24px', maxWidth: '500px', lineHeight: 1.8 }}>
            {this.state.error?.message || '应用遇到了意外错误'}
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={this.handleReset}
              style={{
                padding: '10px 24px',
                border: '2px solid #667eea',
                background: 'transparent',
                color: '#667eea',
                cursor: 'pointer',
                fontFamily: '"Press Start 2P", monospace',
                fontSize: '10px',
              }}
            >
              重试
            </button>
            <button
              onClick={this.handleReload}
              style={{
                padding: '10px 24px',
                border: '2px solid #ff6b6b',
                background: 'transparent',
                color: '#ff6b6b',
                cursor: 'pointer',
                fontFamily: '"Press Start 2P", monospace',
                fontSize: '10px',
              }}
            >
              刷新页面
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
