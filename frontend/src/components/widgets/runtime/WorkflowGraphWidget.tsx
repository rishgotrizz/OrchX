"use client";

import React, { useRef, useImperativeHandle, forwardRef, useEffect, useState } from "react";
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
  const [activeMissionTitle, setActiveMissionTitle] = useState<string>("Active Agentic Mission");

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  useEffect(() => {
    let missionTitle = "Active Agentic Mission";
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('orchx_active_mission');
      if (stored && stored.trim()) missionTitle = stored.trim();
    }
    setActiveMissionTitle(missionTitle);

    if (workflow?.nodes && workflow?.nodes.length > 0) {
      setNodes(workflow.nodes.map((n: any) => ({
        id: n.id,
        position: n.position,
        data: { label: n.label },
        style: { 
          background: n.status === 'running' ? 'rgba(56, 189, 248, 0.15)' : 'var(--color-surface)',
          borderColor: n.status === 'running' ? 'rgb(56, 189, 248)' : 'var(--color-glass-border)',
          color: 'var(--color-text-primary)',
          borderRadius: '8px',
          padding: '10px',
          fontWeight: 600,
          fontSize: '12px'
        }
      })));
      setEdges(workflow.edges.map((e: any) => ({
        id: e.id, source: e.source, target: e.target, animated: e.animated, style: { stroke: '#38bdf8', strokeWidth: 2 }
      })));
    } else {
      // Dynamic active workflow graph nodes
      const dynamicNodes: any[] = [
        {
          id: "n-1",
          type: "input",
          data: { label: `⚡ Trigger: ${missionTitle}` },
          position: { x: 50, y: 150 },
          style: { background: "rgba(168, 85, 247, 0.15)", borderColor: "#a855f7", color: "#f3f4f6", borderRadius: "10px", padding: "10px 14px", fontWeight: 600, fontSize: "12px" }
        },
        {
          id: "n-2",
          data: { label: `🤖 ${missionTitle} Planner` },
          position: { x: 260, y: 80 },
          style: { background: "rgba(56, 189, 248, 0.15)", borderColor: "#38bdf8", color: "#f3f4f6", borderRadius: "10px", padding: "10px 14px", fontWeight: 600, fontSize: "12px" }
        },
        {
          id: "n-3",
          data: { label: "🧠 Groq Llama 3.1 8B (255ms)" },
          position: { x: 500, y: 150 },
          style: { background: "rgba(34, 197, 94, 0.15)", borderColor: "#22c55e", color: "#f3f4f6", borderRadius: "10px", padding: "10px 14px", fontWeight: 600, fontSize: "12px" }
        },
        {
          id: "n-4",
          type: "output",
          data: { label: "🔐 SecretVault RBAC Guard" },
          position: { x: 740, y: 150 },
          style: { background: "rgba(239, 68, 68, 0.15)", borderColor: "#ef4444", color: "#f3f4f6", borderRadius: "10px", padding: "10px 14px", fontWeight: 600, fontSize: "12px" }
        }
      ];

      const dynamicEdges: any[] = [
        { id: "e-1-2", source: "n-1", target: "n-2", animated: true, style: { stroke: "#a855f7", strokeWidth: 2 } },
        { id: "e-2-3", source: "n-2", target: "n-3", animated: true, style: { stroke: "#38bdf8", strokeWidth: 2 } },
        { id: "e-3-4", source: "n-3", target: "n-4", animated: true, style: { stroke: "#22c55e", strokeWidth: 2 } }
      ];

      setNodes(dynamicNodes);
      setEdges(dynamicEdges);
    }
  }, [workflow, setNodes, setEdges]);

  if (error) throw error;
  if (isLoading) return <Panel id="workflow-graph" header="Workflow Graph"><PanelSkeleton /></Panel>;

  return (
    <Panel id="workflow-graph" ref={panelRef} header={`Workflow Graph: ${activeMissionTitle}`} className="h-full">
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
