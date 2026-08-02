"use client";

import React from 'react';
import { Artifact, PreviewSession } from '@/lib/types/preview';

export function HtmlPreviewDriver({ artifact, session }: { artifact: Artifact; session: PreviewSession }) {
  return (
    <div className="w-full h-full bg-white relative">
      <iframe 
        srcDoc={artifact.content} 
        className="w-full h-full border-none absolute inset-0" 
        title="HTML Preview"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}
