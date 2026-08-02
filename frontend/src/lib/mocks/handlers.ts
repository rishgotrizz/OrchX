import { http, HttpResponse } from 'msw';
import { mockDocuments } from '@/lib/mock-data/documents';
import { mockTelemetry as mockMissionTelemetry } from '@/lib/mock-data/telemetry';
import { mockWorkflow as mockMissionWorkflow } from '@/lib/mock-data/workflows';
import { mockTasks } from '@/lib/mock-data/tasks';
import { mockSessions } from '@/lib/mock-data/sessions';
import { mockActivity } from '@/lib/mock-data/activity';
import { mockCredits } from '@/lib/mock-data/credits';
import { mockSuggestions } from '@/lib/mock-data/suggestions';
import { mockFeed } from '@/lib/mock-data/feed';
import { mockArtifacts } from '@/lib/mock-data/preview';
import * as MockRuntime from '@/lib/mock-data/runtime';

export const handlers = [
  // Preview Mock
  http.get('/api/v1/preview/artifacts', () => HttpResponse.json(mockArtifacts)),
  
  // Runtime Mock
  http.get('/api/v1/runtime/kernel', () => HttpResponse.json(MockRuntime.mockKernel)),
  http.get('/api/v1/runtime/memory', () => HttpResponse.json(MockRuntime.mockMemory)),
  http.get('/api/v1/runtime/telemetry', () => HttpResponse.json(MockRuntime.mockTelemetry)),
  http.get('/api/v1/runtime/providers', () => HttpResponse.json(MockRuntime.mockProviders)),
  http.get('/api/v1/runtime/workers', () => HttpResponse.json(MockRuntime.mockWorkers)),
  http.get('/api/v1/runtime/queues', () => HttpResponse.json(MockRuntime.mockQueues)),
  http.get('/api/v1/runtime/agents', () => HttpResponse.json(MockRuntime.mockAgents)),
  http.get('/api/v1/runtime/metrics', () => HttpResponse.json(MockRuntime.mockMetrics)),
  http.get('/api/v1/runtime/alerts', () => HttpResponse.json(MockRuntime.mockAlerts)),
  http.get('/api/v1/runtime/workflow', () => HttpResponse.json(MockRuntime.mockWorkflow)),
  http.get('/api/v1/runtime/executions', () => HttpResponse.json(MockRuntime.mockExecutions)),
  http.get('/api/v1/runtime/router-decision', () => HttpResponse.json(MockRuntime.mockRouterDecision)),
  http.get('/api/v1/runtime/logs', () => HttpResponse.json(MockRuntime.mockLogs)),
  
  // Mission Mock
  http.get('/api/v1/mission/telemetry', () => HttpResponse.json(mockMissionTelemetry)),
  http.get('/api/v1/mission/workflow', () => HttpResponse.json(mockMissionWorkflow)),
  http.get('/api/v1/mission/tasks', () => HttpResponse.json(mockTasks)),
  http.get('/api/v1/mission/sessions', () => HttpResponse.json(mockSessions)),
  http.get('/api/v1/mission/activity', () => HttpResponse.json(mockActivity)),
  http.get('/api/v1/mission/credits', () => HttpResponse.json(mockCredits)),
  http.get('/api/v1/mission/suggestions', () => HttpResponse.json(mockSuggestions)),
  http.get('/api/v1/mission/feed', () => HttpResponse.json(mockFeed)),
  
  // Documents mock
  http.get('/api/v1/documents', () => {
    return HttpResponse.json(mockDocuments);
  }),
  http.get('/api/v1/documents/:id', ({ params }) => {
    const doc = mockDocuments.find(d => d.id === params.id);
    return doc ? HttpResponse.json(doc) : new HttpResponse(null, { status: 404 });
  }),
  http.post('/api/v1/documents', async ({ request }) => {
    const body = await request.json() as object;
    const newDoc = { id: `doc-${Date.now()}`, ...body, createdAt: new Date().toISOString() };
    return HttpResponse.json(newDoc, { status: 201 });
  }),
  http.patch('/api/v1/documents/:id', async ({ request, params }) => {
    const body = await request.json() as object;
    const doc = mockDocuments.find(d => d.id === params.id);
    if (!doc) return new HttpResponse(null, { status: 404 });
    const updated = { ...doc, ...body, updatedAt: new Date().toISOString() };
    return HttpResponse.json(updated);
  }),
  
  // Providers mock
  http.get('/api/v1/providers', () => {
    // In MSW, we can just return a static array representing backend state
    return HttpResponse.json([
      {
        id: 'openrouter',
        name: 'OpenRouter',
        status: 'connected',
        latencyMs: 145,
        health: 'healthy',
        capabilities: ['chat', 'completion'],
        models: [
          { id: 'gpt-4o', name: 'GPT-4o', providerId: 'openrouter', contextLength: 128000, capabilities: ['vision'] },
          { id: 'claude-3.5', name: 'Claude 3.5 Sonnet', providerId: 'openrouter', contextLength: 200000, capabilities: ['coding'] }
        ]
      }
    ]);
  }),
  
  // Settings mock
  http.get('/api/v1/settings/global', () => {
    const item = typeof window !== 'undefined' ? localStorage.getItem(`orchx_settings_global_profile`) : null;
    return HttpResponse.json(item ? JSON.parse(item) : {});
  }),
  http.patch('/api/v1/settings/global', async ({ request }) => {
    const body = await request.json() as object;
    const item = typeof window !== 'undefined' ? localStorage.getItem(`orchx_settings_global_profile`) : null;
    const current = item ? JSON.parse(item) : {};
    const updated = { ...current, ...body };
    if (typeof window !== 'undefined') localStorage.setItem(`orchx_settings_global_profile`, JSON.stringify(updated));
    return HttpResponse.json(updated);
  })
];
