"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const ExecutionTimelineWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { executions, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="execution-timeline" header="Execution Timeline"><ListSkeleton /></Panel>;

  return (
    <Panel id="execution-timeline" ref={panelRef} header="Execution Timeline" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2 relative before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-glass-divider">
        {executions?.map((ex, idx) => (
          <div key={ex.id} className="relative flex items-start space-x-3 group">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 z-10 border-4 border-void bg-surface ${ex.status === 'Queued' ? 'text-text-muted' : 'text-accent-primary'}`}>
              <div className="w-1.5 h-1.5 rounded-full bg-current" />
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-text-primary">{ex.id} ({ex.workflowId})</span>
                <span className="text-xs text-text-muted font-mono">{ex.startedAt}</span>
              </div>
              <span className="text-xs text-accent-primary mt-1 inline-block bg-accent-primary/10 px-1.5 py-0.5 rounded">{ex.status}</span>
            </div>
          </div>
        ))}
      </motion.div>
    </Panel>
  );
});
ExecutionTimelineWidget.displayName = "ExecutionTimelineWidget";
