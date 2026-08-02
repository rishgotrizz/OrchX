"use client";

import React, { useState } from 'react';
import { OrchXDocument } from '@/lib/types/document';
import { useDocumentsContext } from '@/contexts/DocumentsContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export function MarkdownDocumentDriver({ document }: { document: OrchXDocument }) {
  const { updateDocument } = useDocumentsContext();
  const [content, setContent] = useState(document.content);
  const [mode, setMode] = useState<'split' | 'edit' | 'preview'>('split');

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    updateDocument(document.id, e.target.value);
  };

  return (
    <div className="w-full h-full flex flex-col bg-void">
      <div className="flex items-center justify-end p-2 border-b border-glass-border space-x-2 bg-surface">
        <button onClick={() => setMode('edit')} className={`text-xs px-2 py-1 rounded ${mode === 'edit' ? 'bg-accent-primary text-void' : 'text-text-muted hover:bg-surface-hover'}`}>Edit</button>
        <button onClick={() => setMode('split')} className={`text-xs px-2 py-1 rounded ${mode === 'split' ? 'bg-accent-primary text-void' : 'text-text-muted hover:bg-surface-hover'}`}>Split</button>
        <button onClick={() => setMode('preview')} className={`text-xs px-2 py-1 rounded ${mode === 'preview' ? 'bg-accent-primary text-void' : 'text-text-muted hover:bg-surface-hover'}`}>Preview</button>
      </div>
      <div className="flex-1 flex overflow-hidden">
        {(mode === 'edit' || mode === 'split') && (
          <textarea
            className={`h-full p-4 bg-transparent text-gray-300 font-mono text-sm focus:outline-none resize-none ${mode === 'split' ? 'w-1/2 border-r border-glass-border' : 'w-full'}`}
            value={content}
            onChange={handleChange}
            spellCheck={false}
          />
        )}
        {(mode === 'preview' || mode === 'split') && (
          <div className={`h-full p-6 overflow-auto prose prose-invert prose-sm max-w-none ${mode === 'split' ? 'w-1/2' : 'w-full'}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
