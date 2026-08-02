"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { Bot } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const AgentActivityWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { agents, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="agent-activity" header="Agent Activity"><ListSkeleton /></Panel>;

  return (
    <Panel id="agent-activity" ref={panelRef} header="Agent Activity" className="h-full">
      {(!agents || agents.length === 0) ? (
        <EmptyState icon={Bot} title="No Agents" description="No agents are currently active." />
      ) : (
        <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
          {agents.map(a => (
            <div key={a.id} className="p-3 bg-surface border border-glass-border rounded-lg flex flex-col space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <Bot className="w-4 h-4 text-accent-primary" />
                  <span className="text-sm font-medium text-text-primary">{a.name}</span>
                </div>
                <span className={`text-xs px-1.5 py-0.5 rounded font-mono uppercase ${a.status === 'busy' ? 'bg-status-warning/10 text-status-warning' : 'bg-status-success/10 text-status-success'}`}>
                  {a.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-text-muted">
                <div className="flex flex-col"><span>Provider</span><span className="text-text-primary">{a.providerId}</span></div>
                <div className="flex flex-col"><span>Memory</span><span className="text-text-primary">{a.memoryUsageMb} MB</span></div>
                <div className="flex flex-col col-span-2"><span>Tools</span><span className="text-text-primary">{a.activeTools.join(", ")}</span></div>
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </Panel>
  );
});
AgentActivityWidget.displayName = "AgentActivityWidget";
