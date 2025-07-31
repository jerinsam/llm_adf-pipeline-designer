import React, { useState, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge
} from 'reactflow';
import 'reactflow/dist/style.css';
import './PipelineFlow.css';

const PipelineFlow = ({ pipelineData }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [activeTab, setActiveTab] = useState('flow');

  // Debug log to see what data we're receiving
  console.log('PipelineFlow received ', pipelineData);

  // Update flow when pipeline data changes
  useEffect(() => {
    if (!pipelineData) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes = [];
    const newEdges = [];

    // Process nodes from pipeline_flow - handle your exact response structure
    let flowNodes = [];
    let flowEdges = [];
    
    // Check different possible structures
    if (pipelineData.pipeline_flow?.nodes) {
      flowNodes = pipelineData.pipeline_flow.nodes;
      flowEdges = pipelineData.pipeline_flow.edges || [];
    } else if (pipelineData.nodes) {
      flowNodes = pipelineData.nodes;
      flowEdges = pipelineData.edges || [];
    }

    console.log('Processing nodes:', flowNodes);
    console.log('Processing edges:', flowEdges);

    // Create nodes for ADF components
    if (flowNodes && Array.isArray(flowNodes)) {
      flowNodes.forEach((node, index) => {
        const nodeId = node.id || `node-${index}`;
        const nodeType = node.type || 'default';
        const nodeLabel = node.label || node.name || `Node ${index + 1}`;
        
        newNodes.push({
          id: nodeId,
          type: 'default',
          position: { 
            x: (index % 3) * 250 + 50, 
            y: Math.floor(index / 3) * 180 + 50
          },
          data: { 
            label: nodeLabel,
            type: nodeType
          },
          style: {
            background: getNodeColor(nodeType),
            color: 'white',
            border: '2px solid #222',
            width: 200,
            height: 80,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            textAlign: 'center',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            padding: '5px'
          }
        });
      });
    }

    // Create edges for connections
    if (flowEdges && Array.isArray(flowEdges)) {
      flowEdges.forEach((edge, index) => {
        const edgeId = edge.id || `edge-${index}`;
        const sourceId = edge.source || `node-${index}`;
        const targetId = edge.target || `node-${index + 1}`;
        
        newEdges.push({
          id: edgeId,
          source: sourceId,
          target: targetId,
          animated: true,
          style: { stroke: '#0078d4', strokeWidth: 2 },
          label: edge.label || '',
          labelBgPadding: [8, 4],
          labelBgBorderRadius: 4,
          labelBgStyle: { fill: '#ffffff', color: '#333', fillOpacity: 0.9 }
        });
      });
    }

    console.log('Generated nodes:', newNodes);
    console.log('Generated edges:', newEdges);
    
    setNodes(newNodes);
    setEdges(newEdges);
  }, [pipelineData, setNodes, setEdges]);

  const getNodeColor = (type) => {
    const colors = {
      'linked_service': '#742774',
      'dataset': '#107c10',
      'activity': '#0078d4',
      'lookup': '#d83b01',
      'copy': '#0078d4',
      'default': '#605e5c'
    };
    return colors[type?.toLowerCase()] || colors.default;
  };

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds));

  if (!pipelineData) {
    return (
      <div className="pipeline-flow">
        <div className="empty-state">
          <h3>Azure Data Factory Pipeline Generator</h3>
          <p>Describe your data pipeline in the chat to visualize the architecture</p>
          <p className="hint">Example: "Create a pipeline to copy data from SQL Server to Databricks"</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pipeline-flow">
      <div className="pipeline-header">
        <h3>Pipeline Architecture</h3>
        <div className="tabs">
          <button 
            className={activeTab === 'flow' ? 'active' : ''}
            onClick={() => setActiveTab('flow')}
          >
            Flow Diagram
          </button>
          <button 
            className={activeTab === 'json' ? 'active' : ''}
            onClick={() => setActiveTab('json')}
          >
            ADF JSON
          </button>
        </div>
      </div>
      
      {activeTab === 'flow' ? (
        <div className="flow-container">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
          </ReactFlow>
        </div>
      ) : (
        <div className="json-viewer">
          <div className="json-section">
            <h4>Linked Services</h4>
            <pre>{JSON.stringify(pipelineData.json_configs?.linked_services || [], null, 2)}</pre>
          </div>
          <div className="json-section">
            <h4>Datasets</h4>
            <pre>{JSON.stringify(pipelineData.json_configs?.datasets || [], null, 2)}</pre>
          </div>
          <div className="json-section">
            <h4>Pipeline</h4>
            <pre>{JSON.stringify(pipelineData.json_configs?.pipeline || {}, null, 2)}</pre>
          </div>
          <div className="copy-instructions">
            <h4>How to Use</h4>
            <p>Copy the JSON configurations above and paste them in Azure Data Factory:</p>
            <ol>
              <li>Create Linked Services using the Linked Services JSON</li>
              <li>Create Datasets using the Datasets JSON</li>
              <li>Create Pipeline using the Pipeline JSON</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineFlow;