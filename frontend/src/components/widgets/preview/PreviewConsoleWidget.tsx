"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { Terminal } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const PreviewConsoleWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  return (
    <Panel id="preview-console" ref={panelRef} header="Console" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col h-full bg-void p-2 overflow-auto font-mono text-xs">
        <div className="flex items-start space-x-2 text-text-muted mb-1">
          <span className="text-text-secondary shrink-0">12:00:01</span>
          <span>[Info] Artifact compiled successfully.</span>
        </div>
        <div className="flex items-start space-x-2 text-text-muted mb-1">
          <span className="text-text-secondary shrink-0">12:00:02</span>
          <span>[Info] Renderer attached: HtmlPreviewDriver</span>
        </div>
        <div className="flex items-start space-x-2 text-status-warning mb-1">
          <span className="text-status-warning/70 shrink-0">12:00:03</span>
          <span>[Warn] Missing source map for dynamic component.</span>
        </div>
      </motion.div>
    </Panel>
  );
});
PreviewConsoleWidget.displayName = "PreviewConsoleWidget";
