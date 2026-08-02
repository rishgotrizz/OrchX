"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const LiveLogsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const parentRef = useRef<HTMLDivElement>(null);
  const { logs, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const rowVirtualizer = useVirtualizer({
    count: logs?.length || 0,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 32,
    overscan: 5,
  });

  if (error) throw error;
  if (isLoading) return <Panel id="live-logs" header="Live Logs"><ListSkeleton /></Panel>;

  return (
    <Panel id="live-logs" ref={panelRef} header="Live Logs" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="w-full h-full min-h-[300px] overflow-auto bg-void rounded-lg border border-glass-border p-2 font-mono text-xs" ref={parentRef}>
        <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: '100%', position: 'relative' }}>
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const log = logs?.[virtualRow.index];
            const color = log?.level === 'warn' ? 'text-status-warning' : log?.level === 'error' ? 'text-status-error' : 'text-text-secondary';
            return (
              <div
                key={virtualRow.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
                className="flex items-center space-x-3 px-2 hover:bg-surface-hover transition-colors whitespace-nowrap overflow-hidden"
              >
                <span className="text-text-muted shrink-0 w-20 truncate">{log?.timestamp.split('T')[1].split('.')[0]}</span>
                <span className={`uppercase font-bold w-12 shrink-0 ${color}`}>{log?.level}</span>
                <span className="text-text-primary truncate">{log?.message}</span>
              </div>
            );
          })}
        </div>
      </motion.div>
    </Panel>
  );
});
LiveLogsWidget.displayName = "LiveLogsWidget";
