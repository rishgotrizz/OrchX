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

  if (error) throw error;
  if (isLoading) return <Panel id="kernel-status" header="Kernel Status"><CardSkeleton /></Panel>;

  return (
    <Panel id="kernel-status" ref={panelRef} header="Kernel Status" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-4">
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Heartbeat</span>
          <span className={`text-lg font-mono uppercase flex items-center gap-2 ${kernel?.status === 'online' ? 'text-status-success' : 'text-text-muted'}`}>
            <Activity className="w-4 h-4 animate-pulse" /> {kernel?.status || '--'}
          </span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Version</span>
          <span className="text-lg font-mono text-text-primary">{kernel?.version || '--'}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Uptime</span>
          <span className="text-lg font-mono text-text-primary">{kernel?.uptime || '--'}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Workers</span>
          <span className="text-lg font-mono text-text-primary">{workers ? `${workers.length} Active` : '0 Active'}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">CPU Load</span>
          <span className="text-lg font-mono text-text-primary">{telemetry?.cpuUsage !== undefined ? `${telemetry.cpuUsage}%` : '--%'}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Memory</span>
          <span className="text-lg font-mono text-text-primary">{telemetry?.memoryUsage !== undefined ? `${telemetry.memoryUsage}%` : '--%'}</span>
        </div>
      </motion.div>
    </Panel>
  );
});
KernelStatusWidget.displayName = "KernelStatusWidget";
