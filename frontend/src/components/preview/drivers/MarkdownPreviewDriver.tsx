"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { Artifact, PreviewSession } from '@/lib/types/preview';

export function MarkdownPreviewDriver({ artifact, session }: { artifact: Artifact; session: PreviewSession }) {
  return (
    <div className="p-8 w-full h-full overflow-auto prose prose-invert prose-headings:text-accent-primary prose-a:text-accent-hover max-w-none bg-void text-text-primary">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
        {artifact.content}
      </ReactMarkdown>
    </div>
  );
}
