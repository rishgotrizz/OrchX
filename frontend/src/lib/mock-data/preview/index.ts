import * as PreviewTypes from '@/lib/types/preview';

export const mockArtifacts: PreviewTypes.Artifact[] = [
  {
    id: 'art-1',
    name: 'README.md',
    version: 1,
    category: 'document',
    mimeType: 'text/markdown',
    sizeBytes: 1024,
    createdAt: '2026-07-28T10:00:00Z',
    updatedAt: '2026-07-28T10:00:00Z',
    author: 'Researcher-Alpha',
    tags: ['documentation', 'setup'],
    content: '# Project Alpha\\n\\nThis is a generated markdown file.\\n\\n## Features\\n- **Dynamic UI**\\n- **Real-time Engine**\\n\\n| Column 1 | Column 2 |\\n|---|---|\\n| Data 1 | Data 2 |\\n'
  },
  {
    id: 'art-2',
    name: 'config.json',
    version: 2,
    category: 'code',
    mimeType: 'application/json',
    sizeBytes: 450,
    createdAt: '2026-07-28T11:00:00Z',
    updatedAt: '2026-07-28T11:15:00Z',
    author: 'Config-Agent',
    tags: ['configuration', 'system'],
    content: '{\\n  "system": "OrchX",\\n  "version": "1.0",\\n  "enabled": true,\\n  "modules": ["kernel", "preview"]\\n}'
  },
  {
    id: 'art-3',
    name: 'Dashboard Widget',
    version: 1,
    category: 'ui',
    mimeType: 'text/html',
    sizeBytes: 2450,
    createdAt: '2026-07-28T12:00:00Z',
    updatedAt: '2026-07-28T12:00:00Z',
    author: 'Frontend-Bot',
    tags: ['ui', 'component'],
    content: '<div style="padding: 20px; font-family: sans-serif; background: #000; color: #fff; border-radius: 8px; border: 1px solid #333;">\\n  <h2 style="margin:0 0 10px 0; color: #38bdf8;">Widget Title</h2>\\n  <p>This is a rendered HTML artifact preview.</p>\\n  <button style="background: #38bdf8; color: #000; border: none; padding: 8px 16px; border-radius: 4px;">Click Me</button>\\n</div>'
  },
  {
    id: 'art-4',
    name: 'Main.tsx',
    version: 1,
    category: 'code',
    mimeType: 'text/typescript',
    sizeBytes: 800,
    createdAt: '2026-07-28T12:30:00Z',
    updatedAt: '2026-07-28T12:30:00Z',
    author: 'Coder-Agent',
    tags: ['react', 'component'],
    content: 'import React from "react";\\n\\nexport function Main() {\\n  return (\\n    <div className="flex h-screen w-full bg-void">\\n      <span className="text-accent-primary">Hello World</span>\\n    </div>\\n  );\\n}'
  }
];
