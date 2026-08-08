/**
 * 用户菜单组件
 * 显示当前用户信息，提供登出等功能
 */

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, UserInfo } from '../../services/auth';

interface UserMenuProps {
  glassEffect?: boolean;
}

const UserMenu: React.FC<UserMenuProps> = ({ glassEffect = false }) => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // 加载用户信息
  useEffect(() => {
    const user = authAPI.getUserInfo();
    if (user) {
      setUserInfo(user);
    }
  }, []);

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  if (!userInfo) {
    // 未登录，显示登录按钮
    return (
      <div className="user-menu">
        <button 
          className={`pixel-btn ${glassEffect ? 'glass-effect' : ''}`}
          onClick={() => navigate('/login')}
        >
          🔐 登录
        </button>
      </div>
    );
  }

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        className="user-menu-trigger"
        onClick={toggleMenu}
      >
        <span className="user-avatar">
          {userInfo.nickname?.[0] || userInfo.username[0]}
        </span>
        <span className="user-name">{userInfo.nickname || userInfo.username}</span>
        <span className={`dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <div className="user-dropdown">
          <div className="dropdown-header">
            <div className="dropdown-avatar">
              {userInfo.nickname?.[0] || userInfo.username[0]}
            </div>
            <div className="dropdown-info">
              <div className="dropdown-name">{userInfo.nickname || userInfo.username}</div>
              <div className="dropdown-username">@{userInfo.username}</div>
              {userInfo.email && (
                <div className="dropdown-email">{userInfo.email}</div>
              )}
            </div>
          </div>

          <div className="dropdown-divider"></div>

          <div className="dropdown-menu-items">
            <button className="dropdown-item" onClick={() => setIsOpen(false)}>
              👤 个人资料
            </button>
            <button className="dropdown-item" onClick={() => setIsOpen(false)}>
              ⚙️ 设置
            </button>
            <div className="dropdown-divider"></div>
            <button className="dropdown-item dropdown-item--danger" onClick={handleLogout}>
              🚪 退出登录
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
