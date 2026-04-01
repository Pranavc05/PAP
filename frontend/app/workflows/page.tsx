"use client";

import { useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  addEdge,
  useEdgesState,
  useNodesState
} from "reactflow";
import type { Connection, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";

type WorkflowAnalysis = {
  bottleneck_score: number;
  risk_score: number;
  findings: string[];
  recommendations: string[];
};

const API_BASE = "http://localhost:8000/api/v1";
const nodeTypes = ["Start", "Task", "Decision", "Approval", "API", "AI", "End"];

const initialNodes: Node[] = [
  { id: "start-1", type: "input", position: { x: 120, y: 80 }, data: { label: "Start" } },
  { id: "task-1", position: { x: 120, y: 180 }, data: { label: "Task: Collect request" } },
  { id: "end-1", type: "output", position: { x: 120, y: 300 }, data: { label: "End" } }
];

const initialEdges: Edge[] = [
  { id: "e-start-task", source: "start-1", target: "task-1", markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e-task-end", source: "task-1", target: "end-1", markerEnd: { type: MarkerType.ArrowClosed } }
];

function mapLabelToNodeType(label: string): string {
  const normalized = label.toLowerCase();
  const match = nodeTypes.find((type) => normalized.includes(type.toLowerCase()));
  return match?.toLowerCase() ?? "task";
}

export default function WorkflowsPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [analysis, setAnalysis] = useState<WorkflowAnalysis | null>(null);
  const [status, setStatus] = useState("Ready");
  const [workflowId, setWorkflowId] = useState<string | null>(null);

  const exportPayload = useMemo(
    () => ({
      name: "Workflow Lab Draft",
      nodes: nodes.map((node) => ({
        id: node.id,
        type: mapLabelToNodeType(String(node.data?.label ?? "Task")),
        position: node.position,
        data: { label: String(node.data?.label ?? "Task") }
      })),
      edges: edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target
      }))
    }),
    [nodes, edges]
  );

  const addNode = (type: string) => {
    const nextId = `${type.toLowerCase()}-${Date.now()}`;
    const nextNode: Node = {
      id: nextId,
      position: { x: 340, y: 80 + nodes.length * 52 },
      data: { label: type }
    };
    setNodes((current) => [...current, nextNode]);
  };

  const onConnect = (params: Connection) =>
    setEdges((current) =>
      addEdge(
        {
          ...params,
          id: `e-${params.source}-${params.target}-${Date.now()}`,
          markerEnd: { type: MarkerType.ArrowClosed }
        },
        current
      )
    );

  const saveWorkflow = async () => {
    setStatus("Saving workflow...");
    const response = await fetch(`${API_BASE}/workflows`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(exportPayload)
    });
    if (!response.ok) {
      setStatus("Save failed");
      return;
    }
    const data = (await response.json()) as { id: string };
    setWorkflowId(data.id);
    setStatus(`Saved workflow ${data.id.slice(0, 8)}`);
  };

  const loadWorkflow = async () => {
    if (!workflowId) {
      setStatus("Save first to load by ID");
      return;
    }
    setStatus("Loading workflow...");
    const response = await fetch(`${API_BASE}/workflows/${workflowId}`);
    if (!response.ok) {
      setStatus("Load failed");
      return;
    }
    const data = (await response.json()) as {
      nodes: Array<{ id: string; position: { x: number; y: number }; data: { label: string } }>;
      edges: Array<{ id: string; source: string; target: string }>;
    };
    setNodes(
      data.nodes.map((node) => ({
        id: node.id,
        position: node.position,
        data: node.data
      }))
    );
    setEdges(
      data.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        markerEnd: { type: MarkerType.ArrowClosed }
      }))
    );
    setStatus("Workflow loaded");
  };

  const analyzeWorkflow = async () => {
    setStatus("Analyzing workflow...");
    const response = await fetch(`${API_BASE}/workflows/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(exportPayload)
    });
    if (!response.ok) {
      setStatus("Analysis failed");
      return;
    }
    const data = (await response.json()) as WorkflowAnalysis;
    setAnalysis(data);
    setStatus("Analysis complete");
  };

  return (
    <section>
      <h1>Workflow Lab</h1>
      <p>Build a process map, connect steps, save your draft, and run bottleneck analysis.</p>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        {nodeTypes.map((type) => (
          <button key={type} onClick={() => addNode(type)} style={{ padding: "8px 12px" }}>
            Add {type}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={saveWorkflow} style={{ padding: "8px 12px" }}>
          Save
        </button>
        <button onClick={loadWorkflow} style={{ padding: "8px 12px" }}>
          Load
        </button>
        <button onClick={analyzeWorkflow} style={{ padding: "8px 12px" }}>
          Analyze
        </button>
        <span style={{ alignSelf: "center", color: "#334155" }}>{status}</span>
      </div>

      <div style={{ height: 460, border: "1px solid #cbd5e1", borderRadius: 8, background: "#fff" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>

      {analysis ? (
        <article style={{ marginTop: 20, background: "#fff", border: "1px solid #e2e8f0", padding: 16 }}>
          <h3>Bottleneck Analysis</h3>
          <p>
            Bottleneck score: <strong>{analysis.bottleneck_score}</strong> / 100
          </p>
          <p>
            Risk score: <strong>{analysis.risk_score}</strong> / 100
          </p>
          <h4>Findings</h4>
          <ul>
            {analysis.findings.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <h4>Recommendations</h4>
          <ul>
            {analysis.recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
