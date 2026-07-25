'use client';

import { useRef, useState, useMemo, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import type { AgentNode, AgentEdge, GraphNode, GraphLink, ChatMessageData } from '@/types';
import { getNodeColor, getHighlightNodeColor, getEdgeColor, getEdgeWidth, filterEdges } from '@/utils/graphStyles';
import { THEME } from '@/constants/edgeConfig';
import type { ThemeName } from '@/constants/edgeConfig';
import { Badge } from '@/components/atoms';
import { Toolbar, Legend, FloatingModal, ChatSidebar, ThemeTransition } from '@/components/organisms';
import { GraphViewTemplate } from '@/components/templates';
import { fetchGraph, sendChatMessage } from '@/lib/api';
import type { TopologyResult } from '@/lib/api';

const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
  ssr: false,
});

const WELCOME_MSG: ChatMessageData = {
  id: 'welcome',
  role: 'system',
  text: '👋 Bienvenido al asistente de reparación Haceb. Describe el problema técnico que presenta el refrigerador para que el sistema analice el flujo de diagnóstico.',
  timestamp: Date.now(),
};

const generateAssistantResponse = (node: AgentNode): string => {
  if (node.tipo === 'ACCION') {
    return `**Acción:** "${node.label}"\n\n${node.definicion}`;
  }
  if (node.tipo === 'ESTADO') {
    return `**Estado evaluado:** "${node.label}"\n\n${node.definicion}`;
  }
  return `**Información:** "${node.label}"\n\n${node.definicion}`;
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
  const [chatLoading, setChatLoading] = useState(false);

  const [nodes, setNodes] = useState<AgentNode[]>([]);
  const [edges, setEdges] = useState<AgentEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<Set<string>>(new Set());
  const [highlightedEdgeKeys, setHighlightedEdgeKeys] = useState<Set<string>>(new Set());
  const [_lastTopology, setLastTopology] = useState<TopologyResult | null>(null);

  useEffect(() => {
    fetchGraph()
      .then(data => {
        setNodes(data.nodes);
        setEdges(data.edges);
        setLoading(false);
      })
      .catch(err => {
        console.error('fetchGraph failed:', err);
        setLoading(false);
      });
  }, []);

  const p = THEME[theme];

  const handleThemeToggle = useCallback(() => {
    const next: ThemeName = theme === 'dark' ? 'light' : 'dark';
    prevCanvasRef.current = p.canvas;
    setTransitionColor(p.canvas);
    setTheme(next);
    setTimeout(() => setTransitionColor(null), 400);
  }, [theme, p.canvas]);

  const graphNodes: GraphNode[] = useMemo(
    () => nodes.map(n => ({
      ...n,
      highlight: highlightedNodeIds.has(n.id),
    })),
    [nodes, highlightedNodeIds]
  );

  const allFilteredEdges: GraphLink[] = useMemo(
    () => filterEdges(edges, showProceduralOnly),
    [edges, showProceduralOnly]
  );

  const graphLinks: GraphLink[] = useMemo(
    () => allFilteredEdges.map(e => ({
      ...e,
      highlight: highlightedEdgeKeys.has(`${e.source}->${e.target}`),
    })),
    [allFilteredEdges, highlightedEdgeKeys]
  );

  const graphData = useMemo(() => ({
    nodes: graphNodes,
    links: graphLinks,
  }), [graphNodes, graphLinks]);

  const legendItems = useMemo(() => [
    { label: 'Procedural', color: p.edge.procedural },
    { label: 'Informativa', color: p.edge.informativa, dashed: true },
    { label: 'Crítica', color: p.edge.critical, pulse: true },
    { label: 'Resultado', color: '#4fd051', pulse: true },
  ], [p.edge.procedural, p.edge.informativa, p.edge.critical]);

  const hasHighlights = highlightedNodeIds.size > 0;

  const nodeColorFn = useCallback((node: any) => {
    if (!hasHighlights) return getNodeColor(node.tipo, theme);
    if (node.highlight) return getHighlightNodeColor(node.tipo, theme);
    return theme === 'dark' ? '#3a3a3a' : '#d0d0d0';
  }, [theme, hasHighlights]);

  const linkColorFn = useCallback((link: any) => {
    if (!hasHighlights) return getEdgeColor(link, theme);
    if (link.highlight) return getEdgeColor(link, theme);
    return theme === 'dark' ? '#2a2a2a' : '#e0e0e0';
  }, [theme, hasHighlights]);

  const linkWidthFn = useCallback((link: any) => {
    if (!hasHighlights) return getEdgeWidth(link);
    if (!link.highlight) return 0.5;
    return getEdgeWidth(link);
  }, [hasHighlights]);

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

  const handleChatMessage = useCallback(async (text: string, contextNode?: AgentNode) => {
    let fullText = text;
    if (contextNode) {
      fullText = `[Consultando sobre "${contextNode.label}"] ${text}`;
      const contextMsg: ChatMessageData = {
        id: `ctx-${Date.now()}`,
        role: 'system',
        text: `📌 Contexto: nodo **${contextNode.label}** (${contextNode.id}, ${contextNode.tipo})`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, contextMsg]);
    }

    const userMsg: ChatMessageData = {
      id: `user-${Date.now()}`,
      role: 'user',
      text,
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const response = await sendChatMessage(fullText);

      const neighborhoodIds = new Set(response.neighborhood_graph.nodes.map(n => n.id));
      const edgeKeys = new Set(
        response.neighborhood_graph.edges.map(e => `${e.source}->${e.target}`)
      );
      setHighlightedNodeIds(neighborhoodIds);
      setHighlightedEdgeKeys(edgeKeys);
      setLastTopology(response.topology);

      const assistMsg: ChatMessageData = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        text: response.assistant_message,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, assistMsg]);

      if (response.topology.estado === 'DIVERGENTE') {
        const optionsText = response.topology.opciones
          .map((o, i) => `${i + 1}. **${o.leaf_label}** (${(o.ratio * 100).toFixed(0)}%)`)
          .join('\n');
        const optionMsg: ChatMessageData = {
          id: `opt-${Date.now()}`,
          role: 'system',
          text: `🔀 **Múltiples caminos detectados:**\n\n${optionsText}\n\nPor favor indica cuál opción describe mejor el caso.`,
          timestamp: Date.now() + 1,
        };
        setTimeout(() => setMessages(prev => [...prev, optionMsg]), 500);
      }
    } catch (err: any) {
      const errMsg: ChatMessageData = {
        id: `err-${Date.now()}`,
        role: 'system',
        text: `❌ Error: ${err.message || 'No se pudo conectar con el asistente.'}`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setChatLoading(false);
    }
  }, []);

  const handleAskNode = useCallback((node: AgentNode) => {
    setSelectedNode(null);
    setChatOpen(true);
    handleChatMessage(`Cuéntame más sobre "${node.label}" (${node.id})`, node);
  }, [handleChatMessage]);

  const handleSendMessage = useCallback((text: string) => {
    handleChatMessage(text);
  }, [handleChatMessage]);

  const modalFields = selectedNode ? [
    { label: 'Tipo', value: <Badge variant={getBadgeVariant(selectedNode.tipo)}>{selectedNode.tipo}</Badge> },
    { label: 'Definición (CoT)', value: selectedNode.definicion },
    { label: 'Agrupador Canónico', value: selectedNode.agrupador_canonico },
  ] : [];

  const allMessages: ChatMessageData[] = useMemo(() => {
    if (!chatLoading) return messages;
    const loadingMsg: ChatMessageData = {
      id: 'loading',
      role: 'assistant',
      text: '⏳ Analizando consulta con el grafo de conocimiento...',
      timestamp: Date.now(),
    };
    return [...messages, loadingMsg];
  }, [messages, chatLoading]);

  if (loading) {
    return (
      <div style={{
        width: '100vw', height: '100vh',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: p.canvas, color: p.text,
        fontFamily: 'system-ui, sans-serif', fontSize: '1.125rem',
      }}>
        Cargando grafo de conocimiento...
      </div>
    );
  }

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
          nodeColor={nodeColorFn}
          linkColor={linkColorFn}
          linkWidth={linkWidthFn}
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
          onAsk={() => handleAskNode(selectedNode)}
        />
      ) : null}
      legend={<Legend items={legendItems} />}
      sidebar={
        <ChatSidebar
          messages={allMessages}
          open={chatOpen}
          onToggle={() => setChatOpen(o => !o)}
          onSendMessage={handleSendMessage}
        />
      }
    />
  );
};

export default AgentGraphPage;
