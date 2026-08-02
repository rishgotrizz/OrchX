import * as DocTypes from '@/lib/types/document';

export const mockDocuments: DocTypes.OrchXDocument[] = [
  {
    id: 'doc-1',
    title: 'Architecture Blueprint',
    type: 'markdown',
    mimeType: 'text/markdown',
    content: '# Architecture\\n\\nThis is the core architecture.',
    projectId: 'proj-1',
    folderId: 'folder-1',
    version: 3,
    author: 'System Architect',
    createdAt: '2026-07-28T10:00:00Z',
    updatedAt: '2026-07-28T14:00:00Z',
    tags: ['design', 'core']
  },
  {
    id: 'doc-2',
    title: 'Generate Component',
    type: 'prompt',
    mimeType: 'text/plain',
    content: 'Generate a React component for a data table with sorting.',
    projectId: 'proj-1',
    folderId: 'folder-2',
    version: 1,
    author: 'User',
    createdAt: '2026-07-28T11:00:00Z',
    updatedAt: '2026-07-28T11:00:00Z',
    tags: ['ai', 'prompt']
  },
  {
    id: 'doc-3',
    title: 'Deployment Spec',
    type: 'workflow',
    mimeType: 'application/json',
    content: '{\\n  "name": "Deploy",\\n  "steps": []\\n}',
    projectId: 'proj-2',
    folderId: null,
    version: 2,
    author: 'DevOps Agent',
    createdAt: '2026-07-28T12:00:00Z',
    updatedAt: '2026-07-28T13:00:00Z',
    tags: ['ci', 'cd']
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
