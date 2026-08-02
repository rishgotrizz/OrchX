"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Network } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const WorkflowOverviewWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { workflow: data, isLoading, error } = context;

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
    content = <EmptyState icon={Network} title="No Data" description="Nothing to display here yet." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
        <div className="p-4 flex flex-col items-center justify-center space-y-4 border border-glass-border rounded-lg bg-surface">
          <div className="text-sm text-text-secondary">{data.name}</div>
          <div className="flex space-x-2">
            {data.nodes.map((n: any) => (
              <div key={n.id} className="px-3 py-1 rounded bg-void-elevated border border-glass-border text-xs uppercase tracking-wider">{n.type}</div>
            ))}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <Panel id="workflow-overview" ref={panelRef} header="Workflow Overview" className="h-full">
      {content}
    </Panel>
  );
});
WorkflowOverviewWidget.displayName = "WorkflowOverviewWidget";
