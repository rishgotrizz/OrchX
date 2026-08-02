import { registerWidget } from "@/lib/widget-registry";
import { Activity, Server, Clock, Network, Terminal, Bot, List, FileText, BarChart, AlertTriangle, Box } from "lucide-react";
import { KernelStatusWidget } from "./KernelStatusWidget";
import { ProviderActivityWidget } from "./ProviderActivityWidget";
import { ExecutionTimelineWidget } from "./ExecutionTimelineWidget";
import { WorkflowGraphWidget } from "./WorkflowGraphWidget";
import { WorkerPoolWidget } from "./WorkerPoolWidget";
import { AgentActivityWidget } from "./AgentActivityWidget";
import { QueueMonitorWidget } from "./QueueMonitorWidget";
import { LiveLogsWidget } from "./LiveLogsWidget";
import { MetricsWidget } from "./MetricsWidget";
import { AlertsWidget } from "./AlertsWidget";
import { ProviderRouterWidget } from "./ProviderRouterWidget";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read"],
  permissions: ["runtime"],
  refreshPolicy: "event" as const,
  category: "observatory",
};

export function initializeRuntimeWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "kernel-status", title: "Kernel Status", description: "Core system health", icon: Activity, defaultSize: 30, minSize: 20, preferredLayout: "grid", priority: "high", supportedLayouts: ["all"], refreshPolicy: "interval", component: KernelStatusWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "provider-activity", title: "Provider Activity", description: "LLM providers", icon: Server, defaultSize: 40, minSize: 30, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ProviderActivityWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "execution-timeline", title: "Execution Timeline", description: "Live executions", icon: Clock, defaultSize: 40, minSize: 30, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ExecutionTimelineWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "workflow-graph", title: "Workflow Graph", description: "Active DAG", icon: Network, defaultSize: 60, minSize: 40, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: WorkflowGraphWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "worker-pool", title: "Worker Pool", description: "Runtime workers", icon: Terminal, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: WorkerPoolWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "agent-activity", title: "Agent Activity", description: "Active agents", icon: Bot, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: AgentActivityWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "queue-monitor", title: "Queue Monitor", description: "Task queues", icon: List, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: QueueMonitorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "live-logs", title: "Live Logs", description: "Streaming logs", icon: FileText, defaultSize: 40, minSize: 30, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], refreshPolicy: "stream", component: LiveLogsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "metrics", title: "Metrics", description: "Performance metrics", icon: BarChart, defaultSize: 30, minSize: 20, preferredLayout: "grid", priority: "high", supportedLayouts: ["all"], refreshPolicy: "interval", component: MetricsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "alerts", title: "Alerts", description: "System alerts", icon: AlertTriangle, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: AlertsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "provider-router", title: "Provider Router", description: "Intelligent routing decisions", icon: Box, defaultSize: 40, minSize: 30, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ProviderRouterWidget });
}
