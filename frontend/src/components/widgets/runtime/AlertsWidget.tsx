"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useRuntimeContext } from "@/contexts/RuntimeContext";
import { ListSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const AlertsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { alerts, isLoading, error } = useRuntimeContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (error) throw error;
  if (isLoading) return <Panel id="alerts" header="Alerts"><ListSkeleton /></Panel>;

  return (
    <Panel id="alerts" ref={panelRef} header="Alerts" className="h-full border-status-warning/50">
      {(!alerts || alerts.length === 0) ? (
        <EmptyState icon={AlertTriangle} title="No Alerts" description="System is operating normally." />
      ) : (
        <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-2">
          {alerts.map(a => (
            <div key={a.id} className="p-3 bg-status-warning/10 border border-status-warning/20 rounded-lg flex flex-col space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-status-warning capitalize">{a.type} Alert</span>
                <span className="text-xs text-status-warning/70 font-mono">{a.timestamp}</span>
              </div>
              <span className="text-sm text-text-primary">{a.message}</span>
            </div>
          ))}
        </motion.div>
      )}
    </Panel>
  );
});
AlertsWidget.displayName = "AlertsWidget";
