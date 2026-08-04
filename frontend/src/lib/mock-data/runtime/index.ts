import * as RuntimeTypes from '@/lib/types/runtime';

export const mockKernel: RuntimeTypes.Kernel = { status: 'online', version: '1.4.2', uptime: 'Active Session' };
export const mockMemory: RuntimeTypes.Memory = { usedMb: 128, totalMb: 2048, usagePercent: 6 };
export const mockTelemetry: RuntimeTypes.Telemetry = { cpuUsage: 12, memoryUsage: 18 };

export const mockProviders: RuntimeTypes.Provider[] = [
  { id: 'p-1', name: 'Groq LPU', health: { status: 'healthy', latencyMs: 255, errorRate: 0 }, requests: 1, errors: 0, tokens: 420, lastActivity: 'Just now' },
  { id: 'p-2', name: 'OpenRouter', health: { status: 'healthy', latencyMs: 1970, errorRate: 0 }, requests: 1, errors: 0, tokens: 840, lastActivity: 'Just now' }
];

export const mockWorkers: RuntimeTypes.Worker[] = [
  { id: 'groq-agent-01', status: 'busy', assignedTaskId: 'llama-3.1-8b-instant', runtime: 'Groq LPU (255ms)', health: 'healthy' },
  { id: 'openrouter-agent-01', status: 'idle', assignedTaskId: 'meta-llama/llama-3.1-8b-instruct', runtime: 'OpenRouter (1970ms)', health: 'healthy' }
];

export const mockQueues: RuntimeTypes.Queue[] = [
  { id: 'q-high', name: 'High Priority (LLM)', priority: 1, depth: 0, running: 1, pending: 0, completed: 1, retries: 0 }
];

export const mockAgents: RuntimeTypes.Agent[] = [
  { id: 'a-1', name: 'Groq-Agent-01', providerId: 'p-1', currentWorkflowId: 'wf-1', memoryUsageMb: 64, activeTools: ['groq_llama'], status: 'busy' }
];

export const mockMetrics: RuntimeTypes.Metrics = {
  requestsPerSec: 1, tokensPerSec: 420, avgRuntimeMs: 255, latencyMs: 255, cpuUsage: 12, memoryUsage: 18, errorRate: 0
};

export const mockAlerts: RuntimeTypes.Alert[] = [];

export const mockWorkflow: RuntimeTypes.Workflow = {
  id: 'wf-1', name: 'Active Agentic Goal',
  nodes: [
    { id: 'n-1', type: 'trigger', label: '⚡ Trigger: Goal', status: 'completed', position: { x: 50, y: 150 } },
    { id: 'n-2', type: 'agent', label: '🤖 Planner Agent', status: 'running', position: { x: 250, y: 150 } },
    { id: 'n-3', type: 'tool', label: '🧠 Groq Llama 3.1 8B', status: 'completed', position: { x: 450, y: 150 } }
  ],
  edges: [
    { id: 'e-1-2', source: 'n-1', target: 'n-2', animated: true },
    { id: 'e-2-3', source: 'n-2', target: 'n-3', animated: true }
  ]
};

export const mockExecutions: RuntimeTypes.Execution[] = [];

export const mockRouterDecision: RuntimeTypes.RouterDecision = {
  id: 'rd-1', timestamp: new Date().toLocaleTimeString(), incomingRequest: 'Agent Task Routing', taskClassification: 'Code & Reasoning', modelSelection: 'Groq Llama 3.1 8B', fallbackDecision: 'OpenRouter Llama 3.3 70B', currentProvider: 'Groq LPU', latencyMs: 255, retryCount: 0, finalResponse: 'Routing to Groq LPU (255ms latency)'
};

export const mockLogs: RuntimeTypes.LogEntry[] = Array.from({ length: 10 }, (_, i) => ({
  id: `log-${i}`,
  timestamp: new Date(Date.now() - i * 1000).toISOString(),
  level: 'info',
  message: `Kernel runtime telemetry verified trace ID ${Math.random().toString(36).substring(7)}.`,
  source: 'kernel-core'
}));
