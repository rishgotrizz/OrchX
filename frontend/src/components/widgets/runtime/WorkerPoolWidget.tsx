"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Terminal } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

import { mockWorkers } from "@/lib/mock-data/runtime";

export const WorkerPoolWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { workers: rawWorkers, isLoading, error } = useRuntimeContext();

  const workers = (rawWorkers && rawWorkers.length > 0) ? rawWorkers : mockWorkers;

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="worker-pool" header="Worker Pool"><ListSkeleton /></Panel>;

  return (
    <Panel id="worker-pool" ref={panelRef} header="Worker Pool" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
        {workers.map(w => (
          <div key={w.id} className="p-3 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg flex flex-col space-y-1 transition-colors">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-text-primary">{w.id}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded font-mono uppercase ${w.status === 'busy' ? 'bg-status-warning/10 text-status-warning' : w.status === 'idle' ? 'bg-status-success/10 text-status-success' : 'bg-status-error/10 text-status-error'}`}>
                {w.status}
              </span>
            </div>
            <div className="flex justify-between text-xs text-text-muted">
              <span>{w.runtime}</span>
              {w.assignedTaskId && <span>Task: {w.assignedTaskId}</span>}
            </div>
          </div>
        ))}
      </motion.div>
    </Panel>
  );
});
WorkerPoolWidget.displayName = "WorkerPoolWidget";
