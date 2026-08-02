"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { CreditCard } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const CreditsSummaryWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { credits: data, isLoading, error } = context;

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
    content = <EmptyState icon={CreditCard} title="No Data" description="Nothing to display here yet." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-4">
        <div className="flex justify-between text-sm">
          <span className="text-text-secondary">Orchestration Credits</span>
          <span className="text-text-primary font-mono">{data.used.toLocaleString()} / {data.limit.toLocaleString()}</span>
        </div>
        <div className="w-full bg-surface-hover h-2 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${(data.used/data.limit)*100}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="bg-accent-primary h-full shadow-glow" 
          />
        </div>
        <div className="text-xs text-text-muted text-right border-t border-glass-border pt-2">
          Resets {data.resetDate}
        </div>
      </motion.div>
    );
  }

  return (
    <Panel id="credits-summary" ref={panelRef} header="Credits Summary" className="h-full">
      {content}
    </Panel>
  );
});
CreditsSummaryWidget.displayName = "CreditsSummaryWidget";
