'use client';

import { useRef, useState, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import type { AgentNode, GraphNode, GraphLink, ChatMessageData } from '@/types';
import { dummyNodes, dummyEdges } from '@/data/dummyData';
import { getNodeColor, getEdgeColor, getEdgeWidth, filterEdges } from '@/utils/graphStyles';
import { THEME } from '@/constants/edgeConfig';
import type { ThemeName } from '@/constants/edgeConfig';
import { Badge } from '@/components/atoms';
import { Toolbar, Legend, FloatingModal, ChatSidebar, ThemeTransition } from '@/components/organisms';
import { GraphViewTemplate } from '@/components/templates';

const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
  ssr: false,
});

const WELCOME_MSG: ChatMessageData = {
  id: 'welcome',
  role: 'system',
  text: '👋 Bienvenido al visualizador de Chain of Thought. Haz clic en cualquier nodo del grafo para ver los detalles y la respuesta del agente.',
  timestamp: Date.now(),
};

const generateAssistantResponse = (node: AgentNode): string => {
  if (node.tipo === 'ACCION') {
    return `**Acción detectada:** "${node.label}"\n\nEl agente ejecuta esta acción para avanzar en el flujo de cancelación.\n\n${node.definicion}`;
  }
  if (node.tipo === 'ESTADO') {
    return `**Estado evaluado:** "${node.label}"\n\nEl sistema analiza esta condición antes de decidir el siguiente paso.\n\n${node.definicion}`;
  }
  return `**Nodo procesado:** "${node.label}"\n\nInformación registrada en el contexto del agente.\n\n${node.definicion}`;
};

const getBadgeVariant = (tipo: string): 'accion' | 'estado' | 'default' => {
  if (tipo === 'ACCION') return 'accion';
  if (tipo === 'ESTADO') return 'estado';
  return 'default';
};

const AgentGraphPage = () => {
  const graphRef = useRef<any>(null);
  const [theme, setTheme] = useState<ThemeName>('dark');
  const prevCanvasRef = useRef<string>(THEME.dark.canvas);
  const [transitionColor, setTransitionColor] = useState<string | null>(null);
  const [showProceduralOnly, setShowProceduralOnly] = useState(false);
  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessageData[]>([WELCOME_MSG]);

  const p = THEME[theme];

  const handleThemeToggle = useCallback(() => {
    const next = theme === 'dark' ? 'light' : 'dark';
    prevCanvasRef.current = p.canvas;
    setTransitionColor(p.canvas);
    setTheme(next as ThemeName);
    setTimeout(() => setTransitionColor(null), 400);
  }, [theme, p.canvas]);

  const filteredEdges: GraphLink[] = useMemo(
    () => filterEdges(dummyEdges, showProceduralOnly),
    [showProceduralOnly]
  );

  const graphData = useMemo(() => ({
    nodes: dummyNodes as unknown as GraphNode[],
    links: filteredEdges,
  }), [filteredEdges]);

  const legendItems = useMemo(() => [
    { label: 'Procedural', color: p.edge.procedural },
    { label: 'Informativa', color: p.edge.informativa, dashed: true },
    { label: 'Crítica', color: p.edge.critical, pulse: true },
  ], [p.edge.procedural, p.edge.informativa, p.edge.critical]);

  const handleNodeClick = useCallback((node: any) => {
    const agentNode: AgentNode = {
      id: node.id, label: node.label, tipo: node.tipo,
      definicion: node.definicion, agrupador_canonico: node.agrupador_canonico,
    };

    setSelectedNode(agentNode);

    const sysMsg: ChatMessageData = {
      id: `sys-${Date.now()}`,
      role: 'system',
      text: `🔍 Nodo seleccionado: ${agentNode.label} (${agentNode.tipo})  \n\`${agentNode.id}\``,
      timestamp: Date.now(),
    };

    const assistMsg: ChatMessageData = {
      id: `ai-${Date.now()}`,
      role: 'assistant',
      text: generateAssistantResponse(agentNode),
      timestamp: Date.now() + 1,
    };

    setMessages(prev => [...prev, sysMsg]);

    setTimeout(() => {
      setMessages(prev => [...prev, assistMsg]);
    }, 800);
  }, []);

  const handleBackgroundClick = useCallback(() => setSelectedNode(null), []);

  const modalFields = selectedNode ? [
    { label: 'Tipo', value: <Badge variant={getBadgeVariant(selectedNode.tipo)}>{selectedNode.tipo}</Badge> },
    { label: 'Definición (CoT)', value: selectedNode.definicion },
    { label: 'Agrupador Canónico', value: selectedNode.agrupador_canonico },
  ] : [];

  return (
    <GraphViewTemplate
      theme={theme}
      chatOpen={chatOpen}
      toolbar={
        <Toolbar
          showProceduralOnly={showProceduralOnly}
          onToggle={() => setShowProceduralOnly(prev => !prev)}
          theme={theme}
          onThemeToggle={handleThemeToggle}
        />
      }
      graph={
        <ForceGraph3D
          ref={graphRef}
          graphData={graphData}
          nodeId="id"
          nodeLabel="label"
          nodeRelSize={6}
          nodeColor={(node: any) => getNodeColor(node.tipo, theme)}
          linkColor={(link: any) => getEdgeColor(link, theme)}
          linkWidth={(link: any) => getEdgeWidth(link)}
          linkLabel={(link: any) => link.condicion || ''}
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}
          backgroundColor={p.canvas}
          onNodeClick={handleNodeClick}
          onBackgroundClick={handleBackgroundClick}
        />
      }
      themeTransition={transitionColor ? <ThemeTransition fromColor={transitionColor} /> : null}
      modal={selectedNode ? (
        <FloatingModal
          title={selectedNode.label}
          fields={modalFields}
          onClose={() => setSelectedNode(null)}
        />
      ) : null}
      legend={<Legend items={legendItems} />}
      sidebar={
        <ChatSidebar
          messages={messages}
          open={chatOpen}
          onToggle={() => setChatOpen(o => !o)}
        />
      }
    />
  );
};

export default AgentGraphPage;
