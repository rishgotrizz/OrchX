"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useMissionContext } from "@/contexts/MissionContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Lightbulb, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const AiSuggestionsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const context = useMissionContext();
  const { suggestions: data, isLoading, error } = context;

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
    content = <EmptyState icon={Lightbulb} title="No Suggestions" description="No optimization suggestions at this time." />;
  } else {
    content = (
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-3">
        {data.map((item: any) => ( 
          <div key={item.id} className="p-3 bg-accent-primary/5 border border-accent-primary/20 rounded-lg flex space-x-3 items-start group hover:bg-accent-primary/10 transition-colors cursor-pointer">
            <Sparkles className="w-4 h-4 text-accent-primary mt-0.5 shrink-0" />
            <div className="flex flex-col">
              <span className="text-sm font-medium text-accent-primary group-hover:text-accent-hover transition-colors">{item.title}</span>
              <span className="text-xs text-text-secondary leading-relaxed">{item.description}</span>
            </div>
          </div> 
        ))}
      </motion.div>
    );
  }

  return (
    <Panel id="ai-suggestions" ref={panelRef} header="AI Suggestions" className="h-full">
      {content}
    </Panel>
  );
});
AiSuggestionsWidget.displayName = "AiSuggestionsWidget";
