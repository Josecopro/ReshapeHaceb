# AI Agent Chain of Thought Visualizer

A React/TypeScript application that visualizes an AI agent's Chain of Thought (CoT) and reasoning process using a force-directed graph inspired by Obsidian's graph view.

## Features

- **Obsidian-like Canvas**: Full-screen dark mode graph with physics-based node layout
- **Edge Ontology Visualization**:
  - PROCEDURAL edges (causal paths): Solid, prominent lines
  - INFORMATIVA edges (metadata): Dashed, less prominent lines
  - Critical bifurcations: Highlighted in red with glow effect
- **Interactive Node Details**: Click any node to see a floating modal with:
  - Node label
  - Node type (ACCION, ESTADO, INFORMACION)
  - Definition/Thought process (CoT text)
  - Canonical group
- **Graph Context Controls**: Toggle between "Show All Edges" and "Show Procedural Only"
- **Interactive Controls**: Zoom, pan, and rotate the 3D graph

## Tech Stack

- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **react-force-graph-3d** for physics-based graph rendering (Canvas/WebGL)
- **Vite** for fast development and builds

## Project Structure

```
src/
├── AgentGraph.tsx     # Main graph visualization component
├── App.tsx            # Main application component
├── main.tsx           # Entry point
├── index.css          # Tailwind CSS directives and custom styles
├── types.ts           # TypeScript interfaces for AgentNode and AgentEdge
└── dummyData.ts       # Sample data representing a subscription cancellation scenario
```

## Data Model

The application uses the following TypeScript interfaces:

```typescript
interface AgentNode {
  id: string;                    // Canonical lowerCamelCase format
  label: string;                 // Display label
  tipo: string;                  // e.g., "ACCION", "ESTADO"
  definicion: string;            // The actual thought process or definition
  agrupador_canonico: string;    // Grouping category
}

interface AgentEdge {
  source: string;                // Source node ID (origen)
  target: string;                // Target node ID (destino)
  tipo_relacion: "PROCEDURAL" | "INFORMATIVA" | string;
  peso: number;                  // Edge weight/strength
  condicion: string;             // Conditional expression (e.g., "usuario.saldoPendiente > 0")
  es_bifurcacion_critica: boolean; // Whether this is a critical decision point
}
```

## Sample Data

The demo data models a user trying to cancel a subscription with a pending debt, showing:
- Decision points (checking balance, verifying session)
- Conditional branches (based on balance amount)
- Critical bifurcations (when balance > 0 requires payment)
- Procedural flow (main decision path)
- Informational edges (notifications, confirmations)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Customization

To use your own data:
1. Replace the dummy data in `src/dummyData.ts` with your actual AgentNode[] and AgentEdge[] arrays
2. Ensure the data follows the TypeScript interfaces defined in `src/types.ts`
3. The graph will automatically update with your data

## Customization Options

You can modify the visual appearance by adjusting:
- Colors in `AgentGraph.tsx` (node colors, edge colors)
- Node sizes and labels
- Modal styling in the component
- Legend items

## Implementation Details

- Uses `react-force-graph-3d` for WebGL-based force-directed graph rendering
- Implements custom node rendering with Canvas API for precise control
- Uses React state management for UI interactions
- Responsive design that works on various screen sizes
- Smooth animations for modal interactions
- Accessible color contrast in dark mode