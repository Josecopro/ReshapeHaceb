import { NextResponse } from 'next/server';
import nodes from '@/data/nodes.json';
import edges from '@/data/edges.json';
import type { AgentNode, AgentEdge } from '@/types';

export async function GET() {
  const data: { nodes: AgentNode[]; edges: AgentEdge[] } = {
    nodes: nodes as AgentNode[],
    edges: edges as AgentEdge[],
  };
  return NextResponse.json(data);
}
