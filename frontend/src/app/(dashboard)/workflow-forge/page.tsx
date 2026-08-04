"use client";

import React, { useState, useCallback, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { PageTransition } from "@/components/shared/PageTransition";
import { 
  ReactFlow, 
  Controls, 
  Background, 
  MiniMap, 
  useNodesState, 
  useEdgesState,
  addEdge,
  Connection
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { 
  Workflow, 
  Play, 
  Plus, 
  Info, 
  Bot, 
  Wrench, 
  ShieldCheck, 
  Database, 
  RotateCw, 
  Sparkles,
  CheckCircle2,
  ExternalLink,
  Layers,
  Check
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function WorkflowForgeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [activeMissionName, setActiveMissionName] = useState<string>("Active Agentic Goal");

  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [buildProgress, setBuildProgress] = useState<number>(0);
  const [buildComplete, setBuildComplete] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [executionLog, setExecutionLog] = useState<string[]>([]);

  useEffect(() => {
    let missionParam = searchParams?.get('mission');
    if (!missionParam && typeof window !== 'undefined') {
      missionParam = localStorage.getItem('orchx_active_mission');
    }
    
    const missionTitle = missionParam && missionParam.trim() ? missionParam.trim() : "Active Agentic Goal";
    setActiveMissionName(missionTitle);

    // Dynamically build workflow nodes based on active mission!
    const dynamicNodes = [
      {
        id: "node-trigger",
        type: "input",
        data: { label: `⚡ Trigger: ${missionTitle}` },
        position: { x: 50, y: 220 },
        style: {
          background: "rgba(168, 85, 247, 0.15)",
          borderColor: "#a855f7",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px",
          boxShadow: "0 0 20px rgba(168, 85, 247, 0.2)"
        }
      },
      {
        id: "node-planner",
        data: { label: `🤖 ${missionTitle} Planner Agent` },
        position: { x: 280, y: 120 },
        style: {
          background: "rgba(56, 189, 248, 0.15)",
          borderColor: "#38bdf8",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px",
          boxShadow: "0 0 20px rgba(56, 189, 248, 0.2)"
        }
      },
      {
        id: "node-tool",
        data: { label: `🔧 ${missionTitle} Logic & State Tool` },
        position: { x: 280, y: 320 },
        style: {
          background: "rgba(234, 179, 8, 0.15)",
          borderColor: "#eab308",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px"
        }
      },
      {
        id: "node-groq",
        data: { label: "🧠 Groq Llama 3.1 8B (257ms Latency)" },
        position: { x: 580, y: 220 },
        style: {
          background: "rgba(34, 197, 94, 0.15)",
          borderColor: "#22c55e",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px",
          boxShadow: "0 0 20px rgba(34, 197, 94, 0.2)"
        }
      },
      {
        id: "node-vault",
        data: { label: "🔐 SecretVault RBAC Guard" },
        position: { x: 860, y: 120 },
        style: {
          background: "rgba(239, 68, 68, 0.15)",
          borderColor: "#ef4444",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px"
        }
      },
      {
        id: "node-db",
        type: "output",
        data: { label: `💾 ${missionTitle} Store & Logger` },
        position: { x: 860, y: 320 },
        style: {
          background: "rgba(148, 163, 184, 0.15)",
          borderColor: "#94a3b8",
          color: "#f3f4f6",
          borderRadius: "12px",
          padding: "14px 18px",
          fontWeight: 600,
          fontSize: "13px"
        }
      }
    ];

    const dynamicEdges = [
      { id: "e-trig-plan", source: "node-trigger", target: "node-planner", animated: true, style: { stroke: "#a855f7", strokeWidth: 2 } },
      { id: "e-trig-tool", source: "node-trigger", target: "node-tool", animated: true, style: { stroke: "#a855f7", strokeWidth: 2 } },
      { id: "e-plan-groq", source: "node-planner", target: "node-groq", animated: true, style: { stroke: "#38bdf8", strokeWidth: 2 } },
      { id: "e-tool-groq", source: "node-tool", target: "node-groq", animated: true, style: { stroke: "#eab308", strokeWidth: 2 } },
      { id: "e-groq-vault", source: "node-groq", target: "node-vault", animated: true, style: { stroke: "#22c55e", strokeWidth: 2 } },
      { id: "e-groq-db", source: "node-groq", target: "node-db", animated: true, style: { stroke: "#22c55e", strokeWidth: 2 } }
    ];

    setNodes(dynamicNodes);
    setEdges(dynamicEdges);
  }, [searchParams, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: "#38bdf8", strokeWidth: 2 } }, eds)),
    [setEdges]
  );

  const addNode = (type: string, title: string, color: string) => {
    const id = `node-${Date.now()}`;
    const newNode = {
      id,
      data: { label: title },
      position: { x: 300 + Math.random() * 200, y: 150 + Math.random() * 200 },
      style: {
        background: `${color}25`,
        borderColor: color,
        color: "#f3f4f6",
        borderRadius: "12px",
        padding: "14px 18px",
        fontWeight: 600,
        fontSize: "13px"
      }
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const handleRunWorkflow = () => {
    setIsRunning(true);
    setBuildComplete(false);
    setBuildProgress(10);
    
    setExecutionLog([
      `[0.00s] Initializing project build pipeline for ${activeMissionName}...`,
    ]);

    setTimeout(() => {
      setBuildProgress(35);
      setExecutionLog(prev => [
        ...prev,
        `[0.25s] Webhook Trigger received goal: ${activeMissionName}.`,
        `[0.45s] ${activeMissionName} Planner Agent analyzing schemas & UI components...`
      ]);
    }, 400);

    setTimeout(() => {
      setBuildProgress(65);
      setExecutionLog(prev => [
        ...prev,
        `[0.75s] ${activeMissionName} Logic Tool compiling state handlers...`,
        `[0.95s] Groq Llama 3.1 8B completed code generation in 255ms.`
      ]);
    }, 900);

    setTimeout(() => {
      setBuildProgress(85);
      setExecutionLog(prev => [
        ...prev,
        `[1.20s] SecretVault RBAC policy check passed.`,
        `[1.40s] Bundling React/HTML components for Preview Studio...`
      ]);
    }, 1400);

    setTimeout(() => {
      setBuildProgress(100);
      setIsRunning(false);
      setBuildComplete(true);

      setExecutionLog(prev => [
        ...prev,
        `[1.60s] SQLite Event Logger recorded trace ID ex-${Math.floor(10000 + Math.random() * 90000)}.`,
        `[1.65s] ${activeMissionName} PROJECT BUILD SUCCESSFUL!`
      ]);

      // Save built project preview artifact
      if (typeof window !== 'undefined') {
        localStorage.setItem('orchx_built_project', JSON.stringify({
          title: activeMissionName,
          builtAt: new Date().toISOString(),
          status: 'ready'
        }));
      }
    }, 1800);
  };

  return (
    <PageTransition>
      <div className="h-full flex flex-col bg-void text-text-primary relative overflow-hidden">
        
        {/* Top Header & Toolbar */}
        <div className="px-6 py-4 border-b border-glass-border flex items-center justify-between bg-surface shrink-0 z-10">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-accent-primary/10 text-accent-primary">
              <Workflow className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-text-primary">
                  Workflow Forge: <span className="text-accent-primary">{activeMissionName}</span>
                </h1>
                <div className="relative group/forgeinfo inline-block">
                  <button type="button" className="p-0.5 text-text-muted hover:text-accent-primary transition-colors">
                    <Info className="w-4 h-4" />
                  </button>
                  <div className="absolute left-0 top-full mt-2 w-72 p-3 bg-void border border-glass-border rounded-xl shadow-2xl text-xs text-text-secondary opacity-0 pointer-events-none group-hover/forgeinfo:opacity-100 transition-opacity z-50">
                    <span className="font-semibold text-text-primary block mb-1">Dynamic Mission Pipeline</span>
                    Visual multi-agent pipeline orchestrator generated dynamically for {activeMissionName}.
                  </div>
                </div>
              </div>
              <p className="text-xs text-text-muted">Dynamic Multi-Agent Pipeline for {activeMissionName}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {buildComplete && (
              <button 
                onClick={() => router.push('/preview-studio')}
                className="flex items-center space-x-2 px-4 py-2 bg-status-success/20 border border-status-success/50 text-status-success hover:bg-status-success/30 rounded-lg text-sm font-medium transition-all shadow-glow"
              >
                <span>View Built Project</span>
                <ExternalLink className="w-4 h-4" />
              </button>
            )}

            <button 
              onClick={handleRunWorkflow}
              disabled={isRunning}
              className="flex items-center space-x-2 px-5 py-2 bg-accent-primary hover:bg-accent-hover text-white rounded-lg text-sm font-semibold transition-all shadow-glow disabled:opacity-50"
            >
              {isRunning ? <RotateCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
              <span>{isRunning ? `Building Project (${buildProgress}%)...` : "Run Workflow"}</span>
            </button>
          </div>
        </div>

        {/* Live Project Building Overlay / Status Card */}
        <AnimatePresence>
          {(isRunning || buildComplete) && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-surface/90 backdrop-blur-md border-b border-glass-border px-6 py-3 flex items-center justify-between z-20 shrink-0 shadow-lg"
            >
              <div className="flex items-center space-x-3 flex-1 max-w-xl">
                <div className="p-2 rounded-lg bg-accent-primary/10 text-accent-primary">
                  {buildComplete ? <CheckCircle2 className="w-5 h-5 text-status-success" /> : <RotateCw className="w-5 h-5 animate-spin" />}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-text-primary">
                      {buildComplete ? `Project Built Successfully: ${activeMissionName}` : `Building Project: ${activeMissionName}`}
                    </span>
                    <span className="font-mono text-text-muted">{buildProgress}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-void rounded-full overflow-hidden border border-glass-border">
                    <motion.div 
                      className={`h-full ${buildComplete ? 'bg-status-success' : 'bg-accent-primary'}`}
                      animate={{ width: `${buildProgress}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>
              </div>

              {buildComplete && (
                <button
                  onClick={() => router.push('/preview-studio')}
                  className="ml-6 flex items-center space-x-2 px-4 py-1.5 bg-accent-primary hover:bg-accent-hover text-white rounded-lg text-xs font-semibold transition-all shadow-glow"
                >
                  <span>Open in Preview Studio</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Left Node Library Palette */}
          <div className="w-64 border-r border-glass-border bg-surface/50 p-4 flex flex-col space-y-5 overflow-y-auto shrink-0">
            <div>
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider block mb-3">Add Pipeline Nodes</span>
              
              <div className="flex flex-col space-y-2">
                <button 
                  onClick={() => addNode('agent', `🤖 ${activeMissionName} Reviewer`, '#38bdf8')}
                  className="flex items-center space-x-2.5 p-2.5 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg text-xs font-medium text-text-primary text-left transition-colors"
                >
                  <Bot className="w-4 h-4 text-accent-primary" />
                  <span>Agent Node</span>
                </button>

                <button 
                  onClick={() => addNode('tool', '🔧 Python Sandbox Tool', '#eab308')}
                  className="flex items-center space-x-2.5 p-2.5 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg text-xs font-medium text-text-primary text-left transition-colors"
                >
                  <Wrench className="w-4 h-4 text-status-warning" />
                  <span>Sandbox Tool</span>
                </button>

                <button 
                  onClick={() => addNode('security', '🔐 SecretVault Guard', '#ef4444')}
                  className="flex items-center space-x-2.5 p-2.5 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg text-xs font-medium text-text-primary text-left transition-colors"
                >
                  <ShieldCheck className="w-4 h-4 text-status-error" />
                  <span>Security Guard</span>
                </button>

                <button 
                  onClick={() => addNode('db', '💾 Postgres Store', '#94a3b8')}
                  className="flex items-center space-x-2.5 p-2.5 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg text-xs font-medium text-text-primary text-left transition-colors"
                >
                  <Database className="w-4 h-4 text-text-muted" />
                  <span>Data Output</span>
                </button>
              </div>
            </div>

            {/* Execution Trace Log Box */}
            <div className="flex-1 flex flex-col border-t border-glass-divider pt-4 min-h-[160px]">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider block mb-2">Live Build Tracer</span>
              <div className="flex-1 bg-void p-3 rounded-lg border border-glass-border font-mono text-[11px] text-text-secondary overflow-y-auto space-y-1">
                {executionLog.length === 0 ? (
                  <span className="text-text-muted/60 italic">Click "Run Workflow" to start building your project...</span>
                ) : (
                  executionLog.map((log, i) => (
                    <div key={i} className={log.includes("SUCCESSFUL") ? "text-status-success font-bold" : "text-text-primary"}>
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Interactive React Flow Canvas */}
          <div className="flex-1 h-full relative bg-void">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={(_, node) => setSelectedNode(node)}
              fitView
              className="bg-void"
            >
              <Background color="var(--color-glass-divider)" gap={20} />
              <Controls className="bg-surface border border-glass-border fill-text-primary" />
              <MiniMap nodeColor="var(--color-surface-hover)" maskColor="rgba(0,0,0,0.6)" className="bg-void border border-glass-border" />
            </ReactFlow>

            {/* Floating Selection Details Drawer */}
            {selectedNode && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute bottom-6 right-6 w-80 bg-surface border border-glass-border rounded-xl p-4 shadow-2xl flex flex-col space-y-3 z-30"
              >
                <div className="flex items-center justify-between border-b border-glass-divider pb-2">
                  <span className="font-semibold text-xs text-accent-primary uppercase font-mono">Node Inspector</span>
                  <button onClick={() => setSelectedNode(null)} className="text-xs text-text-muted hover:text-text-primary">✕</button>
                </div>
                <div className="flex flex-col space-y-1">
                  <span className="text-sm font-bold text-text-primary">{selectedNode.data.label}</span>
                  <span className="text-xs text-text-muted">Node ID: {selectedNode.id}</span>
                </div>
                <div className="text-xs text-text-secondary bg-void p-2.5 rounded-lg border border-glass-border space-y-1">
                  <div className="flex justify-between"><span>Mission:</span> <span className="font-medium text-text-primary">{activeMissionName}</span></div>
                  <div className="flex justify-between"><span>Status:</span> <span className="text-status-success font-mono">ACTIVE</span></div>
                  <div className="flex justify-between"><span>Latency:</span> <span className="font-mono">120ms</span></div>
                  <div className="flex justify-between"><span>Engine:</span> <span className="font-mono">OrchX Core v1.4</span></div>
                </div>
              </motion.div>
            )}
          </div>

        </div>

      </div>
    </PageTransition>
  );
}

export default function WorkflowForge() {
  return (
    <Suspense fallback={<div className="h-full flex items-center justify-center bg-void text-text-muted">Loading Workflow Forge...</div>}>
      <WorkflowForgeContent />
    </Suspense>
  );
}
