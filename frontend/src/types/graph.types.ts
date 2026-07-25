export interface AgentNode {
  id: string;
  label: string;
  tipo: string;
  definicion: string;
  agrupador_canonico: string;
  cluster_id?: string;
  source_url?: string;
  why?: string[];
}

export interface AgentEdge {
  source: string;
  target: string;
  tipo_relacion: 'PROCEDURAL' | 'INFORMATIVA';
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
  highlight?: boolean;
}

export interface GraphLink {
  source: string;
  target: string;
  tipo_relacion: AgentEdge['tipo_relacion'];
  peso: number;
  condicion: string;
  es_bifurcacion_critica: boolean;
  highlight?: boolean;
}

export interface DbNode {
  id: string;
  label: string;
  cluster_id: string;
  source_url?: string;
  why?: string[];
}

export interface DbEdge {
  source: string;
  target: string;
  edge_type: 'PROCEDURAL' | 'INFORMATIVE';
  cost: number;
}

export function dbNodeToAgentNode(dbNode: DbNode): AgentNode {
  const tipo = inferTipo(dbNode.cluster_id, dbNode.label);
  return {
    id: dbNode.id,
    label: dbNode.label,
    tipo,
    definicion: dbNode.why?.join('\n') ?? '',
    agrupador_canonico: dbNode.cluster_id,
    cluster_id: dbNode.cluster_id,
    source_url: dbNode.source_url,
    why: dbNode.why,
  };
}

export function dbEdgeToAgentEdge(dbEdge: DbEdge): AgentEdge {
  return {
    source: dbEdge.source,
    target: dbEdge.target,
    tipo_relacion: dbEdge.edge_type === 'INFORMATIVE' ? 'INFORMATIVA' : 'PROCEDURAL',
    peso: dbEdge.cost,
    condicion: '',
    es_bifurcacion_critica: false,
  };
}

function inferTipo(clusterId: string, _label: string): string {
  const actionClusters = new Set([
    'compressor', 'sealed_system', 'defrost', 'ventilation',
    'parts', 'icemaker', 'thermostat', 'power',
  ]);
  const stateClusters = new Set([
    'diagnosis', 'electronics', 'mechanical', 'closure',
  ]);
  if (actionClusters.has(clusterId)) return 'ACCION';
  if (stateClusters.has(clusterId)) return 'ESTADO';
  return 'INFORMACION';
}
