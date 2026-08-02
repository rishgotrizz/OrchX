"use client";

import React, { useRef, useImperativeHandle, forwardRef, useMemo } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { PanelSkeleton } from "@/components/core/Skeleton";
import { ReactFlow, Controls, Background, MiniMap, useNodesState, useEdgesState } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const WorkflowGraphWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { workflow, isLoading, error } = useRuntimeContext();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const activeWorkflow = workflow || {
    id: 'wf-1', name: 'Agentic Research',
    nodes: [
      { id: 'n-1', type: 'trigger', label: 'Webhook Trigger', status: 'completed', position: { x: 50, y: 150 } },
      { id: 'n-2', type: 'agent', label: 'Researcher-Alpha', status: 'running', position: { x: 250, y: 150 } },
      { id: 'n-3', type: 'tool', label: 'Web Search', status: 'completed', position: { x: 250, y: 50 } },
      { id: 'n-4', type: 'output', label: 'Database Write', status: 'waiting', position: { x: 450, y: 150 } }
    ],
    edges: [
      { id: 'e-1-2', source: 'n-1', target: 'n-2', animated: false },
      { id: 'e-2-3', source: 'n-2', target: 'n-3', animated: false },
      { id: 'e-2-4', source: 'n-2', target: 'n-4', animated: true }
    ]
  };

  React.useEffect(() => {
    if (activeWorkflow) {
      setNodes(activeWorkflow.nodes.map(n => ({
        id: n.id,
        position: n.position,
        data: { label: n.label },
        style: { 
          background: n.status === 'running' ? 'rgba(56, 189, 248, 0.1)' : 'var(--color-surface)',
          borderColor: n.status === 'running' ? 'rgb(56, 189, 248)' : 'var(--color-glass-border)',
          color: 'var(--color-text-primary)',
          borderRadius: '8px',
          padding: '10px'
        }
      })) as any);
      setEdges(activeWorkflow.edges.map(e => ({
        id: e.id, source: e.source, target: e.target, animated: e.animated, style: { stroke: 'var(--color-glass-divider)' }
      })) as any);
    }
  }, [activeWorkflow, setNodes, setEdges]);

  if (error) throw error;

  return (
    <Panel id="workflow-graph" ref={panelRef} header="Workflow Graph" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="w-full h-full min-h-[300px]">
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView className="bg-void border border-glass-border rounded-lg">
          <Background color="var(--color-glass-divider)" gap={16} />
          <Controls className="bg-surface border border-glass-border fill-text-primary" />
          <MiniMap nodeColor="var(--color-surface-hover)" maskColor="rgba(0,0,0,0.5)" className="bg-void border border-glass-border" />
        </ReactFlow>
      </motion.div>
    </Panel>
  );
});
WorkflowGraphWidget.displayName = "WorkflowGraphWidget";
