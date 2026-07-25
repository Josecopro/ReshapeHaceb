export const EDGE_TYPES = {
  PROCEDURAL: 'PROCEDURAL',
  INFORMATIVA: 'INFORMATIVA',
} as const;

export const NODE_TYPES = {
  ACCION: 'ACCION',
  ESTADO: 'ESTADO',
  INFORMACION: 'INFORMACION',
} as const;

export type ThemeName = 'dark' | 'light';

export const THEME: Record<ThemeName, {
  node: { accion: string; estado: string; informacion: string; default: string };
  edge: { procedural: string; informativa: string; critical: string };
  accent: string;
  bg: string;
  surface: string;
  canvas: string;
  modalBorder: string;
  text: string;
  textMuted: string;
  badgeAccion: string;
  badgeEstado: string;
  badgeDefault: string;
}> = {
  dark: {
    node: { accion: '#3993f4', estado: '#f78612', informacion: '#adadad', default: '#999' },
    edge: { procedural: '#adadad', informativa: '#c2c2c2', critical: '#4fd051' },
    accent: '#28bc37',
    canvas: '#1f1f1f',
    bg: '#000',
    surface: '#3d3d3d',
    modalBorder: '#5c5c5c',
    text: '#fff',
    textMuted: '#999',
    badgeAccion: '#79bcfb',
    badgeEstado: '#febc64',
    badgeDefault: '#d6d6d6',
  },
  light: {
    node: { accion: '#157bf4', estado: '#e57001', informacion: '#707070', default: '#858585' },
    edge: { procedural: '#858585', informativa: '#adadad', critical: '#28bc37' },
    accent: '#08a822',
    canvas: '#f5f5f5',
    bg: '#fff',
    surface: '#fff',
    modalBorder: '#e0e0e0',
    text: '#1f1f1f',
    textMuted: '#858585',
    badgeAccion: '#157bf4',
    badgeEstado: '#e57001',
    badgeDefault: '#707070',
  },
};

export const NODE_SIZES = {
  relSize: 6,
  arrowLength: 6,
  arrowRelPos: 1,
} as const;
