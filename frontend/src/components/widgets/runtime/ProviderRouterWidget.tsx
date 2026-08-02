"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { CardSkeleton } from "@/components/core/Skeleton";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";
import { ArrowRight, Box } from "lucide-react";

export const ProviderRouterWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { routerDecision: r, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="provider-router" header="Provider Router"><CardSkeleton /></Panel>;

  return (
    <Panel id="provider-router" ref={panelRef} header="Provider Router" className="h-full">
      {r && <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-4">
        <div className="p-3 bg-surface border border-glass-border rounded-lg text-sm">
          <div className="text-xs text-text-muted mb-1">Incoming Request</div>
          <div className="font-mono text-text-primary">"{r.incomingRequest}"</div>
        </div>
        
        <div className="flex justify-center"><ArrowRight className="w-4 h-4 text-text-muted rotate-90" /></div>
        
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="p-2 border border-glass-border rounded flex flex-col items-center justify-center text-center">
            <span className="text-xs text-text-muted">Classification</span>
            <span className="text-text-primary mt-1">{r.taskClassification}</span>
          </div>
          <div className="p-2 border border-glass-border rounded flex flex-col items-center justify-center text-center">
            <span className="text-xs text-text-muted">Primary Model</span>
            <span className="text-text-primary mt-1">{r.modelSelection}</span>
          </div>
          <div className="p-2 border border-glass-border rounded flex flex-col items-center justify-center text-center">
            <span className="text-xs text-text-muted">Fallback (if fail)</span>
            <span className="text-text-primary mt-1">{r.fallbackDecision}</span>
          </div>
          <div className="p-2 border border-accent-primary/50 bg-accent-primary/10 rounded flex flex-col items-center justify-center text-center">
            <span className="text-xs text-accent-primary">Selected Provider</span>
            <span className="text-accent-primary font-bold mt-1 flex items-center space-x-1"><Box className="w-3 h-3" /> <span>{r.currentProvider}</span></span>
          </div>
        </div>

        <div className="flex justify-center"><ArrowRight className="w-4 h-4 text-text-muted rotate-90" /></div>

        <div className="p-3 bg-surface border border-glass-border rounded-lg text-sm">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-text-muted">Router Decision Output</span>
            <span className="text-xs text-text-muted font-mono">{r.latencyMs}ms latency</span>
          </div>
          <div className="text-status-success">{r.finalResponse}</div>
        </div>
      </motion.div>}
    </Panel>
  );
});
ProviderRouterWidget.displayName = "ProviderRouterWidget";
