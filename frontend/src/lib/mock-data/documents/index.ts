import * as DocTypes from '@/lib/types/document';

export const mockDocuments: DocTypes.OrchXDocument[] = [
  {
    id: 'doc-1',
    title: 'System Architecture Blueprint',
    type: 'markdown',
    mimeType: 'text/markdown',
    content: `# System Architecture Blueprint\n\n## Core Subsystems\n1. **Kernel Scheduling Engine**: High-concurrency task dispatching.\n2. **SecretVault**: Zero-trust credentials isolation using AES-256-GCM.\n3. **Provider Router**: Circuit-breaker transport routing across OpenRouter, Gemini, and Groq.`,
    projectId: 'proj-1',
    folderId: 'folder-1',
    version: 3,
    author: 'System Architect',
    createdAt: '2026-07-28T10:00:00Z',
    updatedAt: '2026-07-28T14:00:00Z',
    tags: ['engineering', 'core']
  },
  {
    id: 'doc-2',
    title: 'Product Scope & Roadmap',
    type: 'markdown',
    mimeType: 'text/markdown',
    content: `# Product Scope & Roadmap\n\n## Vision\nDeliver enterprise multi-agent orchestration with zero-latency failover.\n\n## Milestones\n- Phase 1: Core Runtime & SecretVault Integration\n- Phase 2: Autonomous Task Execution & Decision Engine\n- Phase 3: Distributed Worker Pool & Edge Deployment`,
    projectId: 'proj-1',
    folderId: 'folder-1',
    version: 2,
    author: 'Product Manager',
    createdAt: '2026-07-28T11:00:00Z',
    updatedAt: '2026-07-28T11:00:00Z',
    tags: ['product', 'roadmap']
  },
  {
    id: 'doc-3',
    title: 'Deployment & Infrastructure Spec',
    type: 'workflow',
    mimeType: 'application/json',
    content: `# Deployment Spec\n\n- **Target Platform**: Vercel Serverless Edge & Docker Runtime\n- **Database**: SQLite / Turso distributed DB\n- **CI/CD Pipeline**: GitHub Actions automated release`,
    projectId: 'proj-2',
    folderId: null,
    version: 2,
    author: 'DevOps Agent',
    createdAt: '2026-07-28T12:00:00Z',
    updatedAt: '2026-07-28T13:00:00Z',
    tags: ['engineering', 'ci-cd']
  },
  {
    id: 'doc-4',
    title: 'Multi-Agent Benchmarking Research',
    type: 'markdown',
    mimeType: 'text/markdown',
    content: `# Multi-Agent Benchmarking Research\n\n## Abstract\nComparative analysis of routing latencies across LLM providers.\n\n- **Groq**: ~250ms latency (Llama 3.1 8B Instant)\n- **OpenRouter**: ~400ms latency (Claude 3.5 Sonnet)\n- **Gemini**: ~300ms latency (Gemini 1.5 Flash)`,
    projectId: 'proj-1',
    folderId: 'folder-2',
    version: 1,
    author: 'AI Research Lead',
    createdAt: '2026-07-29T09:00:00Z',
    updatedAt: '2026-07-29T09:00:00Z',
    tags: ['research', 'benchmarks']
  },
  {
    id: 'doc-5',
    title: 'Autonomous Task Prompt Templates',
    type: 'prompt',
    mimeType: 'text/plain',
    content: `You are OrchX, an autonomous enterprise AI orchestration engine. Break down user goals into concrete technical action plans.`,
    projectId: 'proj-1',
    folderId: 'folder-2',
    version: 1,
    author: 'Prompt Engineer',
    createdAt: '2026-07-29T10:00:00Z',
    updatedAt: '2026-07-29T10:00:00Z',
    tags: ['ai', 'prompts']
  },
  {
    id: 'doc-6',
    title: 'Generated Schema & API Contracts',
    type: 'markdown',
    mimeType: 'text/markdown',
    content: `# Generated Schema Definitions\n\n\`\`\`typescript\nexport interface TaskPlan {\n  id: string;\n  name: string;\n  status: 'Completed' | 'In Progress' | 'Queued';\n  detail: string;\n}\n\`\`\``,
    projectId: 'proj-2',
    folderId: null,
    version: 1,
    author: 'OrchX Code Generator',
    createdAt: '2026-07-29T12:00:00Z',
    updatedAt: '2026-07-29T12:00:00Z',
    tags: ['outputs', 'code']
  }
];

export const mockProjects = [
  { id: 'proj-1', name: 'OrchX Core' },
  { id: 'proj-2', name: 'Infrastructure' }
];

export const mockFolders = [
  { id: 'folder-1', projectId: 'proj-1', name: 'Docs' },
  { id: 'folder-2', projectId: 'proj-1', name: 'Prompts' }
];
