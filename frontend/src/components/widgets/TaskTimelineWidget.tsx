"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { ListTodo } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const TaskTimelineWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { tasks: data, isLoading, error } = context;

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
    content = <EmptyState icon={ListTodo} title="No Data" description="Nothing to display here yet." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col">
        {data.map((item: any) => ( 
          <div key={item.id} className="p-3 border-b border-glass-border last:border-0 flex justify-between items-center text-sm hover:bg-surface transition-colors">
            <span className="text-text-primary">{item.title}</span>
            <span className="text-text-muted font-mono text-xs">{item.status}</span>
          </div> 
        ))}
      </motion.div>
    );
  }

  return (
    <Panel id="task-timeline" ref={panelRef} header="Task Timeline" className="h-full">
      {content}
    </Panel>
  );
});
TaskTimelineWidget.displayName = "TaskTimelineWidget";
