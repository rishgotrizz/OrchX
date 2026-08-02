"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";
import { usePreviewContext } from "@/contexts/PreviewContext";

export const PreviewStatisticsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, artifacts } = usePreviewContext();
  const currentArtifact = artifacts.find(a => a.id === session.artifactId);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (!currentArtifact) return <Panel id="preview-statistics" header="Statistics" className="h-full"><div/></Panel>;

  return (
    <Panel id="preview-statistics" ref={panelRef} header="Statistics" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-3 text-sm">
        <div className="flex flex-col p-2 bg-surface border border-glass-border rounded">
          <span className="text-xs text-text-muted">Lines</span>
          <span className="font-mono text-text-primary mt-1">{currentArtifact.content.split('\\n').length}</span>
        </div>
        <div className="flex flex-col p-2 bg-surface border border-glass-border rounded">
          <span className="text-xs text-text-muted">Words</span>
          <span className="font-mono text-text-primary mt-1">{currentArtifact.content.split(/\\s+/).length}</span>
        </div>
        <div className="flex flex-col p-2 bg-surface border border-glass-border rounded col-span-2">
          <span className="text-xs text-text-muted">Render Time</span>
          <span className="font-mono text-text-primary mt-1">42ms (Cache Hit)</span>
        </div>
      </motion.div>
    </Panel>
  );
});
PreviewStatisticsWidget.displayName = "PreviewStatisticsWidget";
