export interface AgentNode {
  id: string;
  label: string;
  tipo: string;
  definicion: string;
  agrupador_canonico: string;
}

export interface AgentEdge {
  source: string;
  target: string;
  tipo_relacion: 'PROCEDURAL' | 'INFORMATIVA' | string;
  peso: number;
  condicion: string;
  es_bifurcacion_critica: boolean;
}

export interface GraphNode extends AgentNode {
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  tipo_relacion: string;
  peso: number;
  condicion: string;
  es_bifurcacion_critica: boolean;
}

export interface NodeSchema {
  id: string;
  label: string;
  cluster_id: string;
}

export interface EdgeSchema {
  source: string;
  target: string;
  edge_type: 'PROCEDURAL' | 'INFORMATIVE';
  cost: number;
}
