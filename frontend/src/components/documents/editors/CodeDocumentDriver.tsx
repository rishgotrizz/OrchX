"use client";

import React, { useState } from 'react';
import { OrchXDocument } from '@/lib/types/document';
import { useDocumentsContext } from '@/contexts/DocumentsContext';

export function CodeDocumentDriver({ document }: { document: OrchXDocument }) {
  const { updateDocument } = useDocumentsContext();
  const [content, setContent] = useState(document.content);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    updateDocument(document.id, e.target.value);
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#1e1e1e]">
      <textarea
        className="w-full h-full p-4 bg-transparent text-gray-300 font-mono text-sm focus:outline-none resize-none"
        value={content}
        onChange={handleChange}
        spellCheck={false}
      />
    </div>
  );
}
