"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { PanelSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Zap } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";
import { Button } from "@/components/core/Button";

export const QuickActionsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { isLoading, error } = context;

  useImperativeHandle(ref, () => ({
    refresh: () => { /* trigger fetch */ },
    focus: () => panelRef.current?.focus(),
    expand: () => panelRef.current?.expand(),
    collapse: () => panelRef.current?.collapse(),
  }));

  if (error) throw error;

  let content;
  if (isLoading) {
    content = <PanelSkeleton />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="grid grid-cols-2 gap-2">
        <Button variant="default" className="w-full">New Mission</Button>
        <Button variant="ghost" className="w-full border border-glass-border hover:bg-status-error/10 hover:text-status-error">Halt Kernel</Button>
        <Button variant="ghost" className="w-full border border-glass-border">Snapshot</Button>
        <Button variant="ghost" className="w-full border border-glass-border">Export Logs</Button>
      </motion.div>
    );
  }

  return (
    <Panel id="quick-actions" ref={panelRef} header="Quick Actions" className="h-full">
      {content}
    </Panel>
  );
});
QuickActionsWidget.displayName = "QuickActionsWidget";
