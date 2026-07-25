export interface AgentNode {
  id: string; // Canonical lowerCamelCase format (e.g., "cancelarSuscripcion")
  label: string;
  tipo: string; // e.g., "ACCION", "ESTADO"
  definicion: string; // The actual thought process or definition
  agrupador_canonico: string;
}

export interface AgentEdge {
  source: string; // maps to "origen" in my DB
  target: string; // maps to "destino" in my DB
  tipo_relacion: "PROCEDURAL" | "INFORMATIVA" | string;
  peso: number;
  condicion: string; // e.g., "usuario.saldoPendiente > 0"
  es_bifurcacion_critica: boolean;
}