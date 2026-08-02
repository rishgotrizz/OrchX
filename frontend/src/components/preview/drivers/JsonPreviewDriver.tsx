"use client";

import React from 'react';
import { Artifact, PreviewSession } from '@/lib/types/preview';
import { CodePreviewDriver } from './CodePreviewDriver';

export function JsonPreviewDriver({ artifact, session }: { artifact: Artifact; session: PreviewSession }) {
  return <CodePreviewDriver artifact={artifact} session={session} lang="json" />;
}
