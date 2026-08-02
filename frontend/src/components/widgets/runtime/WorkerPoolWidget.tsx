"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Terminal } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const WorkerPoolWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { workers, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const activeWorkers = (workers && workers.length > 0) ? workers : [
    { id: 'w-1', status: 'busy', assignedTaskId: 't-12', runtime: 'NodeJS v20', health: 'healthy' },
    { id: 'w-2', status: 'idle', runtime: 'Python 3.11', health: 'healthy' },
    { id: 'w-3', status: 'offline', runtime: 'Go 1.22', health: 'unhealthy' }
  ];

  if (error) throw error;

  return (
    <Panel id="worker-pool" ref={panelRef} header="Worker Pool" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
        {activeWorkers.map(w => (
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
