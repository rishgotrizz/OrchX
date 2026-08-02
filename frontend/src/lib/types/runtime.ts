export type ExecutionStatus = 'Queued' | 'Running' | 'Thinking' | 'Tool Calling' | 'Completed' | 'Failed' | 'Cancelled' | 'Retrying';

export interface Execution {
  id: string;
  workflowId: string;
  status: ExecutionStatus;
  startedAt: string;
  completedAt?: string;
  error?: string;
  duration?: number;
}

export interface WorkflowNode {
  id: string;
  type: string;
  label: string;
  status: 'running' | 'completed' | 'waiting' | 'failed' | 'queued';
  position: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface Task {
  id: string;
  title: string;
  status: ExecutionStatus;
  timestamp: string;
}

export interface ProviderHealth {
  status: 'healthy' | 'degraded' | 'offline';
  latencyMs: number;
  errorRate: number;
}

export interface Provider {
  id: string;
  name: string;
  health: ProviderHealth;
  requests: number;
  errors: number;
  tokens: number;
  lastActivity: string;
}

export interface Agent {
  id: string;
  name: string;
  providerId: string;
  currentWorkflowId: string;
  memoryUsageMb: number;
  activeTools: string[];
  status: 'idle' | 'busy' | 'offline';
}

export interface Worker {
  id: string;
  status: 'idle' | 'busy' | 'offline';
  assignedTaskId?: string;
  runtime: string;
  health: 'healthy' | 'unhealthy';
}

export interface Kernel {
  status: 'online' | 'offline' | 'restarting';
  version: string;
  uptime: string;
}

export interface Memory {
  usedMb: number;
  totalMb: number;
  usagePercent: number;
}

export interface Telemetry {
  cpuUsage: number;
  memoryUsage: number;
}

export interface Queue {
  id: string;
  name: string;
  priority: number;
  depth: number;
  running: number;
  pending: number;
  completed: number;
  retries: number;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  source: string;
}

export interface Logs {
  entries: LogEntry[];
}

export interface Metrics {
  requestsPerSec: number;
  tokensPerSec: number;
  avgRuntimeMs: number;
  latencyMs: number;
  cpuUsage: number;
  memoryUsage: number;
  errorRate: number;
}

export interface Alert {
  id: string;
  type: 'warning' | 'failure' | 'provider' | 'memory' | 'queue';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface Session {
  id: string;
  userId: string;
  activeProject: string;
}

export interface RuntimeStatistics {
  activeExecutions: number;
  totalExecutions: number;
}

export interface RouterDecision {
  id: string;
  timestamp: string;
  incomingRequest: string;
  taskClassification: string;
  modelSelection: string;
  fallbackDecision: string;
  currentProvider: string;
  latencyMs: number;
  retryCount: number;
  finalResponse: string;
}
