"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Users } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const ActiveSessionsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { sessions: data, isLoading, error } = context;

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
    content = <EmptyState icon={Users} title="No Active Sessions" description="No users currently active." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col">
        {data.map((item: any) => ( 
          <div key={item.id} className="p-3 border-b border-glass-border last:border-0 flex justify-between items-center text-sm hover:bg-surface transition-colors">
            <div className="flex flex-col">
              <span className="text-text-primary">{item.user}</span>
              <span className="text-xs text-text-muted">{item.project}</span>
            </div>
            <span className="text-text-secondary font-mono text-xs">{item.uptime}</span>
          </div> 
        ))}
      </motion.div>
    );
  }

  return (
    <Panel id="active-sessions" ref={panelRef} header="Active Sessions" className="h-full">
      {content}
    </Panel>
  );
});
ActiveSessionsWidget.displayName = "ActiveSessionsWidget";
