import { useEffect, useState, useRef } from 'react';

interface ThemeTransitionProps {
  fromColor: string;
}

const ThemeTransition = ({ fromColor }: ThemeTransitionProps) => {
  const [visible, setVisible] = useState(true);
  const elRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;

    const frame = requestAnimationFrame(() => {
      el.style.opacity = '0';
    });

    const timer = setTimeout(() => setVisible(false), 350);

    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(timer);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      ref={elRef}
      className="theme-overlay"
      style={{ backgroundColor: fromColor }}
    />
  );
};

export default ThemeTransition;
