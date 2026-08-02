"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { History } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";
import { usePreviewContext } from "@/contexts/PreviewContext";

export const VersionHistoryWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session } = usePreviewContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  return (
    <Panel id="version-history" ref={panelRef} header="Version History" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col space-y-4 p-2 relative before:absolute before:inset-y-0 before:left-[19px] before:w-px before:bg-glass-divider">
        {[3, 2, 1].map((v, i) => (
          <div key={v} className="relative flex items-start space-x-3">
            <div className={`w-4 h-4 rounded-full border-[3px] border-void bg-surface shrink-0 z-10 ${i === 0 ? 'border-accent-primary' : 'border-text-muted'}`} />
            <div className="flex flex-col -mt-1">
              <span className={`text-sm font-medium ${i === 0 ? 'text-text-primary' : 'text-text-secondary'}`}>Version {v}</span>
              <span className="text-xs text-text-muted mt-0.5">{i === 0 ? 'Current' : '2 hours ago'}</span>
            </div>
          </div>
        ))}
      </motion.div>
    </Panel>
  );
});
VersionHistoryWidget.displayName = "VersionHistoryWidget";
