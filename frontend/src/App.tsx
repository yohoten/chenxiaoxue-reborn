/**
 * 主应用组件 - 支持路由和认证
 * 路由级代码分割：Login / Register / MainApp 按需加载
 * 包含全局 ErrorBoundary 防止白屏
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { authAPI } from './services/auth';
import { ErrorBoundary } from './components/Common/ErrorBoundary';

const MainApp = lazy(() => import('./MainApp'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));

const PageLoading: React.FC = () => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    height: '100vh', background: '#1a1a2e', color: '#e0e0e0',
    fontFamily: '"Press Start 2P", monospace', fontSize: '12px',
  }}>
    加载中...
  </div>
);

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authAPI.isAuthenticated();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

// 公开路由（已登录用户访问时重定向到主页）
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authAPI.isAuthenticated();
  if (isAuthenticated) return <Navigate to="/" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={<PageLoading />}>
          <Routes>
          <Route
            path="/login"
            element={<PublicRoute><Login /></PublicRoute>}
          />
          <Route
            path="/register"
            element={<PublicRoute><Register /></PublicRoute>}
          />
          <Route
            path="/*"
            element={<ProtectedRoute><MainApp /></ProtectedRoute>}
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
