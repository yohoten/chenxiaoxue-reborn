/**
 * 统一 HTTP 客户端
 * 基于 axios，所有 API 调用共享同一个实例，统一管理 Token 和错误处理。
 */

import axios from 'axios';

const httpClient = axios.create({
  headers: { 'Content-Type': 'application/json' },
});

// 请求拦截器：自动附加 Token
httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理 401
httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default httpClient;
