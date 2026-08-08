/**
 * Chen筱雪 Reborn - 应用入口
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/pixel-theme.css';
import './styles/global.css';
import './styles/ui-polish.css';

const root = document.getElementById('root');
if (!root) {
  throw new Error('找不到 root 元素！请确保 index.html 中存在 <div id="root"></div>');
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
