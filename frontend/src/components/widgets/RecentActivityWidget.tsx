"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { History } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const RecentActivityWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { activity: data, isLoading, error } = context;

  useImperativeHandle(ref, () => ({
    refresh: () => { /* trigger fetch */ },
    focus: () => panelRef.current?.focus(),
    expand: () => panelRef.current?.expand(),
    collapse: () => panelRef.current?.collapse(),
  }));

  if (error) throw error;

  let content;
  if (isLoading) {
    content = <ListSkeleton />;
  } else if (!data || data.length === 0) {
    content = <EmptyState icon={History} title="No Recent Activity" description="Logs will appear here." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col">
        {data.map((item: any) => ( 
          <div key={item.id} className="p-3 border-b border-glass-border last:border-0 flex flex-col space-y-1 hover:bg-surface transition-colors">
            <span className="text-sm text-text-primary leading-tight">{item.message}</span>
            <span className="text-xs text-text-muted">{item.time}</span>
          </div> 
        ))}
      </motion.div>
    );
  }

  return (
    <Panel id="recent-activity" ref={panelRef} header="Recent Activity" className="h-full">
      {content}
    </Panel>
  );
});
RecentActivityWidget.displayName = "RecentActivityWidget";
