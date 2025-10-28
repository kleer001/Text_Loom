import { useEffect, useState } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls,
  type Node as RFNode,
  type Edge as RFEdge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { WorkspaceData, Node } from './types';

const API_URL = 'http://127.0.0.1:8000/api/v1/workspace';

function App() {
  const [nodes, setNodes] = useState<RFNode[]>([]);
  const [edges, setEdges] = useState<RFEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch workspace data on mount
    fetch(API_URL)
      .then(res => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then((data: WorkspaceData) => {
        // Convert nodes to ReactFlow format
        const rfNodes: RFNode[] = data.nodes.map((node: Node) => ({
          id: node.path,
          type: 'default',
          position: { x: node.position[0], y: node.position[1] },
          data: { 
            label: (
              <div style={{ padding: '10px' }}>
                <div style={{ fontWeight: 'bold' }}>{node.name}</div>
                <div style={{ fontSize: '0.8em', color: '#666' }}>{node.type}</div>
              </div>
            )
          },
        }));

        // Convert connections to ReactFlow edges
        const rfEdges: RFEdge[] = data.connections.map(conn => ({
          id: conn.id,
          source: conn.source_node_path,
          target: conn.target_node_path,
          sourceHandle: `out-${conn.source_output_index}`,
          targetHandle: `in-${conn.target_input_index}`,
        }));

        setNodes(rfNodes);
        setEdges(rfEdges);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.5em'
      }}>
        Loading workspace...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        color: 'red'
      }}>
        <h2>Error Loading Workspace</h2>
        <p>{error}</p>
        <p style={{ fontSize: '0.9em', color: '#666' }}>
          Make sure the API is running at {API_URL}
        </p>
      </div>
    );
  }

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <div style={{ 
        position: 'absolute', 
        top: 10, 
        left: 10, 
        zIndex: 10,
        background: 'white',
        padding: '10px 20px',
        borderRadius: '5px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ margin: 0 }}>TextLoom - Phase 1</h3>
        <p style={{ margin: '5px 0 0 0', fontSize: '0.9em', color: '#666' }}>
          {nodes.length} nodes, {edges.length} connections
        </p>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default App;