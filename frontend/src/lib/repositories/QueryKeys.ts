export const QueryKeys = {
  documents: {
    all: ['documents'] as const,
    list: (projectId: string) => ['documents', 'list', projectId] as const,
    detail: (id: string) => ['documents', 'detail', id] as const,
  },
  settings: {
    all: ['settings'] as const,
    profile: (id: string) => ['settings', 'profile', id] as const,
  },
  providers: {
    all: ['providers'] as const,
    models: (providerId: string) => ['providers', 'models', providerId] as const,
  },
  runtime: {
    metrics: ['runtime', 'metrics'] as const,
    executions: ['runtime', 'executions'] as const,
  },
  mission: {
    workflows: ['mission', 'workflows'] as const,
    tasks: ['mission', 'tasks'] as const,
  },
  preview: {
    artifacts: ['preview', 'artifacts'] as const,
    session: (id: string) => ['preview', 'session', id] as const,
  }
};
