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

  React.useEffect(() => {
    if (workflow) {
      setNodes(workflow.nodes.map(n => ({
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
      setEdges(workflow.edges.map(e => ({
        id: e.id, source: e.source, target: e.target, animated: e.animated, style: { stroke: 'var(--color-glass-divider)' }
      })) as any);
    }
  }, [workflow, setNodes, setEdges]);

  if (error) throw error;
  if (isLoading) return <Panel id="workflow-graph" header="Workflow Graph"><PanelSkeleton /></Panel>;

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
