import type { DbNode, DbEdge, AgentNode, AgentEdge } from '@/types/graph.types';
import { dbNodeToAgentNode, dbEdgeToAgentEdge } from '@/types/graph.types';

const BASE_URL = 'http://localhost:8000';

export interface TopologyOption {
  leaf_id: string;
  leaf_label: string;
  leaf_why: string[];
  count: number;
  ratio: number;
}

export interface TopologyResult {
  estado: 'CONVERGENTE' | 'DIVERGENTE' | 'SIN_CAMINO';
  origen: string | null;
  camino_seleccionado: string[] | null;
  hoja_mayoritaria: TopologyOption | null;
  opciones: TopologyOption[];
}

export interface ChatResponse {
  assistant_message: string;
  neighborhood_graph: { nodes: DbNode[]; edges: DbEdge[] };
  extracted_graph: { nodes: DbNode[]; edges: DbEdge[] };
  topology: TopologyResult;
}

export interface GraphResponse {
  nodes: DbNode[];
  edges: DbEdge[];
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export async function fetchGraph(): Promise<{ nodes: AgentNode[]; edges: AgentEdge[] }> {
  const data = await request<GraphResponse>('/api/graph');
  return {
    nodes: data.nodes.map(dbNodeToAgentNode),
    edges: data.edges.map(dbEdgeToAgentEdge),
  };
}

export interface NodeReasoningResponse {
  node_id: string;
  label: string;
  reasoning: string;
  why: string[];
  source_url?: string;
  predecessors: string[];
  successors: string[];
}

export async function fetchNodeReasoning(nodeId: string, userContext?: string): Promise<NodeReasoningResponse> {
  return request<NodeReasoningResponse>('/api/node-reasoning', {
    method: 'POST',
    body: JSON.stringify({ node_id: nodeId, user_context: userContext }),
  });
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return request<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

