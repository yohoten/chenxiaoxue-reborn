/**
 * 认证 API 服务
 */

import httpClient from './httpClient';

const AUTH_BASE = '/api/auth';

// 类型定义
export interface RegisterData {
  username: string;
  email?: string;
  password: string;
  nickname?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface UserInfo {
  id: number;
  username: string;
  email?: string;
  nickname?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface UpdateUserData {
  email?: string;
  nickname?: string;
  avatar_url?: string;
  password?: string;
}

// API 方法
export const authAPI = {
  register: async (data: RegisterData): Promise<UserInfo> => {
    const response = await httpClient.post(`${AUTH_BASE}/register`, data);
    return response.data;
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await httpClient.post(`${AUTH_BASE}/login`, data);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_info', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  getCurrentUser: async (): Promise<UserInfo> => {
    const response = await httpClient.get(`${AUTH_BASE}/me`);
    return response.data;
  },

  updateProfile: async (data: UpdateUserData): Promise<UserInfo> => {
    const response = await httpClient.put(`${AUTH_BASE}/me`, data);
    const currentUser = JSON.parse(localStorage.getItem('user_info') || '{}');
    localStorage.setItem('user_info', JSON.stringify({ ...currentUser, ...response.data }));
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await httpClient.post(`${AUTH_BASE}/logout`);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
    }
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  getUserInfo: (): UserInfo | null => {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  },

  getToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
};
