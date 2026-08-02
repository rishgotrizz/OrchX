"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const MetricsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { metrics, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="metrics" header="Metrics"><CardSkeleton /></Panel>;

  return (
    <Panel id="metrics" ref={panelRef} header="Metrics" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-4">
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Req/sec</span>
          <span className="text-lg font-mono text-text-primary">{metrics?.requestsPerSec.toFixed(1)}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Tokens/sec</span>
          <span className="text-lg font-mono text-text-primary">{metrics?.tokensPerSec.toLocaleString()}</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Avg Runtime</span>
          <span className="text-lg font-mono text-text-primary">{metrics?.avgRuntimeMs}ms</span>
        </div>
        <div className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg">
          <span className="text-xs text-text-muted mb-1">Error Rate</span>
          <span className={`text-lg font-mono ${(metrics?.errorRate || 0) > 0.05 ? 'text-status-error' : 'text-status-success'}`}>
            {((metrics?.errorRate || 0) * 100).toFixed(2)}%
          </span>
        </div>
      </motion.div>
    </Panel>
  );
});
MetricsWidget.displayName = "MetricsWidget";
