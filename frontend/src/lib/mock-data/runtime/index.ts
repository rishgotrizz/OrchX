import * as RuntimeTypes from '@/lib/types/runtime';

export const mockKernel: RuntimeTypes.Kernel = { status: 'online', version: '1.4.2', uptime: '14d 2h 44m' };
export const mockMemory: RuntimeTypes.Memory = { usedMb: 4096, totalMb: 8192, usagePercent: 50 };
export const mockTelemetry: RuntimeTypes.Telemetry = { cpuUsage: 35, memoryUsage: 50 };

export const mockProviders: RuntimeTypes.Provider[] = [
  { id: 'p-1', name: 'OpenRouter', health: { status: 'healthy', latencyMs: 120, errorRate: 0.01 }, requests: 15420, errors: 12, tokens: 2040000, lastActivity: '2s ago' },
  { id: 'p-2', name: 'Gemini', health: { status: 'healthy', latencyMs: 85, errorRate: 0 }, requests: 4320, errors: 0, tokens: 500000, lastActivity: '1s ago' },
  { id: 'p-3', name: 'Groq', health: { status: 'degraded', latencyMs: 340, errorRate: 0.05 }, requests: 1200, errors: 4, tokens: 100000, lastActivity: '5m ago' },
  { id: 'p-4', name: 'Cloudflare Workers AI', health: { status: 'healthy', latencyMs: 45, errorRate: 0 }, requests: 8900, errors: 0, tokens: 800000, lastActivity: '1s ago' }
];

export const mockWorkers: RuntimeTypes.Worker[] = [
  { id: 'w-1', status: 'busy', assignedTaskId: 't-12', runtime: 'NodeJS v20', health: 'healthy' },
  { id: 'w-2', status: 'idle', runtime: 'Python 3.11', health: 'healthy' },
  { id: 'w-3', status: 'offline', runtime: 'Go 1.22', health: 'unhealthy' }
];

export const mockQueues: RuntimeTypes.Queue[] = [
  { id: 'q-high', name: 'High Priority (LLM)', priority: 1, depth: 14, running: 4, pending: 10, completed: 4200, retries: 2 },
  { id: 'q-med', name: 'Medium Priority (Extract)', priority: 2, depth: 45, running: 12, pending: 33, completed: 18400, retries: 15 },
  { id: 'q-low', name: 'Low Priority (Batch)', priority: 3, depth: 250, running: 2, pending: 248, completed: 50000, retries: 0 }
];

export const mockAgents: RuntimeTypes.Agent[] = [
  { id: 'a-1', name: 'Researcher-Alpha', providerId: 'p-1', currentWorkflowId: 'wf-1', memoryUsageMb: 240, activeTools: ['web_search', 'read_file'], status: 'busy' },
  { id: 'a-2', name: 'Data-Extractor', providerId: 'p-2', currentWorkflowId: 'wf-2', memoryUsageMb: 120, activeTools: ['json_parse'], status: 'idle' }
];

export const mockMetrics: RuntimeTypes.Metrics = {
  requestsPerSec: 42.5, tokensPerSec: 1240, avgRuntimeMs: 450, latencyMs: 85, cpuUsage: 35, memoryUsage: 50, errorRate: 0.012
};

export const mockAlerts: RuntimeTypes.Alert[] = [
  { id: 'al-1', type: 'provider', severity: 'medium', message: 'Groq API latency degraded.', timestamp: '10:04 AM' },
  { id: 'al-2', type: 'queue', severity: 'low', message: 'Batch queue depth > 200.', timestamp: '10:00 AM' }
];

export const mockWorkflow: RuntimeTypes.Workflow = {
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

export const mockExecutions: RuntimeTypes.Execution[] = [
  { id: 'ex-1', workflowId: 'wf-1', status: 'Tool Calling', startedAt: '10:00:00 AM', duration: 12000 },
  { id: 'ex-2', workflowId: 'wf-2', status: 'Queued', startedAt: '10:02:00 AM' }
];

export const mockRouterDecision: RuntimeTypes.RouterDecision = {
  id: 'rd-1', timestamp: '10:04:12 AM', incomingRequest: 'Summarize 50 page PDF', taskClassification: 'Large Context Summarization', modelSelection: 'Gemini 1.5 Pro', fallbackDecision: 'OpenRouter (Claude 3 Opus)', currentProvider: 'Gemini', latencyMs: 240, retryCount: 0, finalResponse: 'Routing to Gemini (1m context available)'
};

export const mockLogs: RuntimeTypes.LogEntry[] = Array.from({ length: 100 }, (_, i) => ({
  id: `log-${i}`,
  timestamp: new Date(Date.now() - i * 1000).toISOString(),
  level: i % 10 === 0 ? 'warn' : 'info',
  message: `Kernel log event trace ID ${Math.random().toString(36).substring(7)} processed.`,
  source: 'kernel-core'
}));
