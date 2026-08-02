"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";
import { Server } from "lucide-react";
import { ProviderTopologyScene } from "@/components/experience/ProviderTopologyScene";

export const ProviderActivityWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { providers, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="provider-activity" header="Provider Activity"><ListSkeleton /></Panel>;

  return (
    <Panel id="provider-activity" ref={panelRef} header="Provider Activity" className="h-full">
      <div className="flex flex-col space-y-4 h-full p-2 overflow-y-auto">
        <div className="flex-shrink-0 h-48 w-full">
          <ProviderTopologyScene />
        </div>
        <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
          {providers?.map(p => (
            <div key={p.id} className="p-3 bg-surface hover:bg-surface-hover border border-glass-border rounded-lg flex flex-col space-y-2 transition-colors">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <Server className="w-4 h-4 text-text-secondary" />
                  <span className="text-sm font-semibold text-text-primary">{p.name}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded font-mono uppercase ${p.health.status === 'healthy' ? 'bg-status-success/10 text-status-success' : 'bg-status-warning/10 text-status-warning'}`}>
                  {p.health.status}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs text-text-muted pt-1 border-t border-glass-border">
                <div className="flex flex-col"><span>Latency</span><span className="text-text-primary font-mono">{p.health.latencyMs}ms</span></div>
                <div className="flex flex-col"><span>Tokens</span><span className="text-text-primary font-mono">{(p.tokens / 1000).toFixed(1)}k</span></div>
                <div className="flex flex-col"><span>Errors</span><span className="text-text-primary font-mono">{p.errors}</span></div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </Panel>
  );
});
ProviderActivityWidget.displayName = "ProviderActivityWidget";
