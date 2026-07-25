import type { MouseEventHandler, ReactNode } from 'react';
import './Overlay.scss';

interface OverlayProps {
  onClick?: MouseEventHandler<HTMLDivElement>;
  blur?: boolean;
  color?: string;
  className?: string;
  children?: ReactNode;
}

const Overlay = ({ onClick, blur = false, color, className = '', children }: OverlayProps) => (
  <div
    className={`overlay${blur ? ' overlay--blur' : ''} ${className}`.trim()}
    style={color ? { backgroundColor: color } : undefined}
    onClick={onClick}
  >
    {children}
  </div>
);

export default Overlay;
