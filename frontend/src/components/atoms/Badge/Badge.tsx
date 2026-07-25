import type { ReactNode } from 'react';
import './Badge.scss';

interface BadgeProps {
  variant: 'accion' | 'estado' | 'default';
  children: ReactNode;
}

const Badge = ({ variant, children }: BadgeProps) => (
  <span className={`badge badge-${variant}`}>{children}</span>
);

export default Badge;
