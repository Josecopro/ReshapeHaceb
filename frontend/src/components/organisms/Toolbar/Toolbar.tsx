import { Icon } from '@/components/atoms';
import type { ThemeName } from '@/constants/edgeConfig';
import './Toolbar.scss';

interface ToolbarProps {
  showProceduralOnly: boolean;
  onToggle: () => void;
  theme: ThemeName;
  onThemeToggle: () => void;
}

const Toolbar = ({ showProceduralOnly, onToggle, theme, onThemeToggle }: ToolbarProps) => (
  <div className="toolbar">
    <button
      className="toolbar__btn toolbar__btn--icon"
      onClick={onThemeToggle}
      title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
    >
      <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={18} />
    </button>

    <button
      className={`toolbar__btn${showProceduralOnly ? ' toolbar__btn--active' : ''}`}
      onClick={onToggle}
    >
      <span className="toolbar__dot" />
      {showProceduralOnly ? 'Todas las aristas' : 'Solo procedurales'}
    </button>
  </div>
);

export default Toolbar;
