"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Cpu } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const SystemHealthWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { telemetry: data, isLoading, error } = context;

  useImperativeHandle(ref, () => ({
    refresh: () => { /* trigger fetch */ },
    focus: () => panelRef.current?.focus(),
    expand: () => panelRef.current?.expand(),
    collapse: () => panelRef.current?.collapse(),
  }));

  if (error) throw error;

  let content;
  if (isLoading) {
    content = <CardSkeleton />;
  } else if (!data) {
    content = <EmptyState icon={Cpu} title="No Data" description="Telemetry offline." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-4">
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">CPU Load</span>
          <span className="text-xl font-mono text-text-primary">{data.cpuUsage}%</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Memory</span>
          <span className="text-xl font-mono text-text-primary">{data.memoryUsage}%</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Active Nodes</span>
          <span className="text-xl font-mono text-text-primary">{data.activeNodes}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Kernel Status</span>
          <div className="mt-1">
            <div className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-status-success/10 text-status-success uppercase tracking-wider">{data.kernelStatus}</div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <Panel id="system-health" ref={panelRef} header="System Health" className="h-full">
      {content}
    </Panel>
  );
});
SystemHealthWidget.displayName = "SystemHealthWidget";
