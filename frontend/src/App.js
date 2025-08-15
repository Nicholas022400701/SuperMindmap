import React, { useState, useEffect, useRef } from 'react';
import { ForceGraph3D } from 'react-force-graph';
import { getGraphData, addKeyword, exportNode, deleteNode } from './services/api';
import './App.css';

function App() {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const fgRef = useRef();

  // Function to fetch and update graph data
  const fetchGraph = async () => {
    const graphData = await getGraphData();
    // The ObjectRoot node can make the graph layout weird, let's hide it.
    const filteredNodes = graphData.nodes.filter(node => node.name !== 'ObjectRoot');
    const filteredLinks = graphData.links.filter(link => link.source !== 1 && link.target !== 1);

    // The API returns source/target as numbers, but react-force-graph needs them to be node objects or ids.
    // It handles ID-based links automatically.
    setData({ nodes: filteredNodes, links: filteredLinks });
  };

  // Fetch initial data on component mount
  useEffect(() => {
    fetchGraph();
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    setLoading(true);
    setError('');
    try {
      await addKeyword(keyword);
      setKeyword(''); // Clear input
      await fetchGraph(); // Refresh the graph
    } catch (err) {
      setError(err.message || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    // If clicking the same node, deselect it. Otherwise, select the new node.
    if (selectedNode && selectedNode.id === node.id) {
      setSelectedNode(null);
    } else {
      setSelectedNode(node);
    }
  };

  const handleExport = async () => {
    if (!selectedNode) return;
    try {
      await exportNode(selectedNode.id);
    } catch (err) {
      setError(err.message || 'Failed to export.');
    }
  };

  const handleDelete = async () => {
    if (!selectedNode) return;
    // A simple confirmation before deleting
    if (window.confirm(`Are you sure you want to delete the node "${selectedNode.name}" and its entire subtree?`)) {
      setLoading(true);
      setError('');
      try {
        await deleteNode(selectedNode.id);
        setSelectedNode(null); // Deselect the node
        await fetchGraph(); // Refresh the graph
      } catch (err) {
        setError(err.message || 'Failed to delete.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Super Mind Map System</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Enter a keyword"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Mind Map'}
          </button>
        </form>
        {error && <p className="error-message">{error}</p>}
      </header>

      {selectedNode && (
        <div className="node-actions">
          <h2>Selected Node: {selectedNode.name}</h2>
          <button onClick={handleExport}>Export Subtree</button>
          <button onClick={handleDelete} className="delete-button">Delete Tree</button>
        </div>
      )}

      <div className="graph-container">
        <ForceGraph3D
          ref={fgRef}
          graphData={data}
          nodeLabel="name"
          nodeAutoColorBy="name"
          linkDirectionalParticles={2}
          linkDirectionalParticleWidth={1.5}
          onEngineStop={() => fgRef.current.zoomToFit(400)}
          onNodeClick={handleNodeClick}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

            // Draw background rectangle
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

            // Draw text
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'black';
            ctx.fillText(label, node.x, node.y);

            node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            const bckgDimensions = node.__bckgDimensions;
            bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
          }}
        />
      </div>
    </div>
  );
}

export default App;
