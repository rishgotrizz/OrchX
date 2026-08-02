"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Activity } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const MissionFeedWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { feed: data, isLoading, error } = context;

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
    content = <EmptyState icon={Activity} title="No Data" description="Nothing to display here yet." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
        {data.map((item: any) => ( <div key={item.id} className="p-2 bg-surface hover:bg-surface-hover border border-glass-border rounded flex justify-between text-sm transition-colors"><span className="text-text-primary truncate">{item.event}</span><span className="text-text-muted font-mono text-xs shrink-0">{item.time}</span></div> ))}
      </motion.div>
    );
  }

  return (
    <Panel id="mission-feed" ref={panelRef} header="Mission Feed" className="h-full">
      {content}
    </Panel>
  );
});
MissionFeedWidget.displayName = "MissionFeedWidget";
