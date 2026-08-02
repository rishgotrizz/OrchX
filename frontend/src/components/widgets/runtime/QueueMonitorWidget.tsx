"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { List } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const QueueMonitorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { queues, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="queue-monitor" header="Queue Monitor"><ListSkeleton /></Panel>;

  return (
    <Panel id="queue-monitor" ref={panelRef} header="Queue Monitor" className="h-full">
      {(!queues || queues.length === 0) ? (
        <EmptyState icon={List} title="No Queues" description="No active queues found." />
      ) : (
        <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-3">
          {queues.map(q => (
            <div key={q.id} className="p-3 bg-surface border border-glass-border rounded-lg flex flex-col space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-text-primary">{q.name}</span>
                <span className="text-xs text-text-muted bg-void-elevated px-2 py-0.5 rounded border border-glass-border font-mono">P{q.priority}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="flex flex-col"><span className="text-text-muted">Depth</span><span className="text-text-primary font-mono">{q.depth}</span></div>
                <div className="flex flex-col"><span className="text-text-muted">Pending</span><span className="text-status-warning font-mono">{q.pending}</span></div>
                <div className="flex flex-col"><span className="text-text-muted">Running</span><span className="text-accent-primary font-mono">{q.running}</span></div>
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </Panel>
  );
});
QueueMonitorWidget.displayName = "QueueMonitorWidget";
