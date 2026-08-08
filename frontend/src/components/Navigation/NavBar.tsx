/**
 * 导航栏组件 - 紧凑像素风格
 * 使用 PixelButton 实现的导航切换
 */

import { PixelButton } from '../Common/PixelButton';

interface NavItem {
  id: string;
  label: string;
}

interface NavBarProps {
  items: NavItem[];
  activeId: string;
  onSelect: (id: string) => void;
  glassEffect?: boolean;
}

export function NavBar({ items, activeId, onSelect, glassEffect = false }: NavBarProps) {
  return (
    <div className={`nav-bar ${glassEffect ? 'glass-effect' : ''}`}>
      {items.map((item) => (
        <PixelButton
          key={item.id}
          variant="nav"
          active={activeId === item.id}
          onClick={() => onSelect(item.id)}
          style={{
            width: '100%',
            justifyContent: 'flex-start',
            textAlign: 'left',
            fontSize: 12,
            padding: '8px 12px',
            gap: 6,
          }}
        >
          {item.label}
        </PixelButton>
      ))}
    </div>
  );
}
