"use client";

import React, { useRef, useImperativeHandle, forwardRef, useEffect } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { Activity } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const KernelStatusWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { kernel, telemetry, workers, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {},
    mount: () => {},
    refresh: () => {},
    sleep: () => {},
    resume: () => {},
    destroy: () => {},
    onVisibilityChange: () => {},
    onPermissionChange: () => {},
  }));

  const activeKernel = kernel || { status: 'online', version: '1.4.2', uptime: '14d 2h 44m' };
  const activeTelemetry = telemetry || { cpuUsage: 35, memoryUsage: 50 };
  const activeWorkers = workers || [
    { id: 'w-1', status: 'busy', assignedTaskId: 't-12', runtime: 'NodeJS v20', health: 'healthy' },
    { id: 'w-2', status: 'idle', runtime: 'Python 3.11', health: 'healthy' },
    { id: 'w-3', status: 'offline', runtime: 'Go 1.22', health: 'unhealthy' }
  ];

  if (error) throw error;

  return (
    <Panel id="kernel-status" ref={panelRef} header="Kernel Status" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-4">
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Heartbeat</span>
          <span className="text-lg font-mono text-status-success uppercase flex items-center gap-2">
            <Activity className="w-4 h-4 animate-pulse" /> {activeKernel.status}
          </span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Version</span>
          <span className="text-lg font-mono text-text-primary">{activeKernel.version}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Uptime</span>
          <span className="text-lg font-mono text-text-primary">{activeKernel.uptime}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Workers</span>
          <span className="text-lg font-mono text-text-primary">{activeWorkers.length} Active</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">CPU Load</span>
          <span className="text-lg font-mono text-text-primary">{activeTelemetry.cpuUsage}%</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Memory</span>
          <span className="text-lg font-mono text-text-primary">{activeTelemetry.memoryUsage}%</span>
        </div>
      </motion.div>
    </Panel>
  );
});
KernelStatusWidget.displayName = "KernelStatusWidget";
