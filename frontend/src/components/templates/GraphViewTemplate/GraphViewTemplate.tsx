import type { ReactNode } from 'react';
import type { ThemeName } from '@/constants/edgeConfig';
import './GraphViewTemplate.scss';

interface GraphViewTemplateProps {
  theme: ThemeName;
  chatOpen: boolean;
  toolbar: ReactNode;
  graph: ReactNode;
  sidebar: ReactNode;
  legend: ReactNode;
  modal: ReactNode | null;
  themeTransition: ReactNode | null;
}

const GraphViewTemplate = ({
  theme,
  chatOpen,
  toolbar,
  graph,
  sidebar,
  legend,
  modal,
  themeTransition,
}: GraphViewTemplateProps) => (
  <div className="graph-container" data-theme={theme}>
    {toolbar}

    <div className={`graph-container__main${chatOpen ? ' graph-container__main--shifted' : ''}`}>
      {graph}
    </div>

    {themeTransition}
    {modal}
    {legend}
    {sidebar}
  </div>
);

export default GraphViewTemplate;
