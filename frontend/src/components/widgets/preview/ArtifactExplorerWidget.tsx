"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { usePreviewContext } from "@/contexts/PreviewContext";
import { File, FileText, FileJson, FileCode, Folder } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const ArtifactExplorerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { artifacts, session, setSession } = usePreviewContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const getIcon = (mimeType: string) => {
    if (mimeType.includes('markdown')) return <FileText className="w-4 h-4 text-accent-primary" />;
    if (mimeType.includes('json')) return <FileJson className="w-4 h-4 text-status-warning" />;
    if (mimeType.includes('html') || mimeType.includes('typescript')) return <FileCode className="w-4 h-4 text-status-success" />;
    return <File className="w-4 h-4 text-text-secondary" />;
  };

  return (
    <Panel id="artifact-explorer" ref={panelRef} header="Artifact Explorer" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col">
        <div className="flex items-center space-x-2 p-2 text-sm text-text-secondary font-medium">
          <Folder className="w-4 h-4" />
          <span>Project Root</span>
        </div>
        <div className="flex flex-col pl-4 mt-1 border-l border-glass-border ml-4 space-y-1">
          {artifacts.map(a => {
            const isActive = session.artifactId === a.id;
            return (
              <button
                key={a.id}
                onClick={() => setSession(s => ({ ...s, artifactId: a.id }))}
                className={`flex items-center space-x-2 px-2 py-1.5 rounded text-sm transition-colors text-left ${isActive ? 'bg-accent-primary/10 text-accent-primary' : 'hover:bg-surface-hover text-text-primary'}`}
              >
                {getIcon(a.mimeType)}
                <span className="truncate">{a.name}</span>
              </button>
            );
          })}
        </div>
      </motion.div>
    </Panel>
  );
});
ArtifactExplorerWidget.displayName = "ArtifactExplorerWidget";
