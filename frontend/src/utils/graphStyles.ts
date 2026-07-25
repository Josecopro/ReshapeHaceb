import { THEME, NODE_TYPES } from '@/constants/edgeConfig';
import type { ThemeName } from '@/constants/edgeConfig';
import type { GraphLink } from '@/types';

export const getNodeColor = (tipo: string, theme: ThemeName = 'dark'): string => {
  const p = THEME[theme].node;
  switch (tipo) {
    case NODE_TYPES.ACCION: return p.accion;
    case NODE_TYPES.ESTADO: return p.estado;
    case NODE_TYPES.INFORMACION: return p.informacion;
    default: return p.default;
  }
};

export const getBadgeClass = (tipo: string): string => {
  switch (tipo) {
    case NODE_TYPES.ACCION: return 'badge-accion';
    case NODE_TYPES.ESTADO: return 'badge-estado';
    default: return 'badge-default';
  }
};

export const getEdgeColor = (link: GraphLink, theme: ThemeName = 'dark'): string => {
  const p = THEME[theme].edge;
  if (link.es_bifurcacion_critica) return p.critical;
  if (link.tipo_relacion === 'PROCEDURAL') return p.procedural;
  return p.informativa;
};

export const getEdgeWidth = (link: GraphLink): number => {
  if (link.es_bifurcacion_critica) {
    return link.tipo_relacion === 'PROCEDURAL' ? 5 : 3;
  }
  if (link.tipo_relacion === 'PROCEDURAL') return 3;
  return 2;
};

export const filterEdges = (edges: GraphLink[], proceduralOnly: boolean): GraphLink[] => {
  if (proceduralOnly) return edges.filter(e => e.tipo_relacion === 'PROCEDURAL');
  return edges;
};
