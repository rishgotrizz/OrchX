"use client";

import React, { useEffect, useState } from 'react';
import { Artifact, PreviewSession } from '@/lib/types/preview';
import { createHighlighter, Highlighter } from 'shiki';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/motion';

let cachedHighlighter: Highlighter | null = null;

export function CodePreviewDriver({ artifact, session, lang = 'typescript' }: { artifact: Artifact; session: PreviewSession; lang?: string }) {
  const [html, setHtml] = useState<string>('');

  useEffect(() => {
    let isMounted = true;
    async function highlight() {
      try {
        if (!cachedHighlighter) {
          cachedHighlighter = await createHighlighter({
            themes: ['github-dark'],
            langs: ['typescript', 'json', 'yaml', 'html', 'css', 'javascript'],
          });
        }
        const htmlOutput = cachedHighlighter?.codeToHtml(artifact.content, { lang, theme: 'github-dark' }) || `<pre><code>${artifact.content}</code></pre>`;
        if (isMounted) setHtml(htmlOutput);
      } catch (e) {
        if (isMounted) setHtml(`<pre><code>${artifact.content}</code></pre>`); // fallback
      }
    }
    highlight();
    return () => { isMounted = false; };
  }, [artifact.content, lang]);

  return (
    <motion.div variants={fadeIn} initial="initial" animate="animate" className="w-full h-full p-6 overflow-auto bg-[#24292e]">
      {html ? (
        <div dangerouslySetInnerHTML={{ __html: html }} className="text-sm font-mono leading-relaxed" />
      ) : (
        <div className="text-text-muted text-sm font-mono">Loading syntax highlighter...</div>
      )}
    </motion.div>
  );
}
