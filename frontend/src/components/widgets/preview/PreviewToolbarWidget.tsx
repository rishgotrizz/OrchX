"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { usePreviewContext } from "@/contexts/PreviewContext";
import { Monitor, Tablet, Smartphone, Maximize, SplitSquareHorizontal, Download, Share2 } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const PreviewToolbarWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, setSession } = usePreviewContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const devices = [
    { id: 'desktop', icon: Monitor },
    { id: 'tablet', icon: Tablet },
    { id: 'mobile', icon: Smartphone }
  ];

  return (
    <Panel id="preview-toolbar" ref={panelRef} className="h-full !bg-surface/50">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex items-center justify-between w-full h-full px-2">
        <div className="flex items-center space-x-1 bg-void rounded p-1 border border-glass-border">
          {devices.map(d => (
            <button
              key={d.id}
              onClick={() => setSession(s => ({ ...s, deviceProfile: d.id as any }))}
              className={`p-1.5 rounded transition-colors ${session.deviceProfile === d.id ? 'bg-accent-primary text-void' : 'text-text-muted hover:text-text-primary hover:bg-surface-hover'}`}
              title={d.id}
            >
              <d.icon className="w-4 h-4" />
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
           <button className="p-1.5 rounded border border-glass-border bg-void text-text-secondary hover:text-text-primary hover:border-text-muted transition-colors flex items-center space-x-2 text-sm px-3">
             <SplitSquareHorizontal className="w-4 h-4" />
             <span>Compare</span>
           </button>
           <button className="p-1.5 rounded border border-glass-border bg-void text-text-secondary hover:text-text-primary hover:border-text-muted transition-colors">
             <Download className="w-4 h-4" />
           </button>
           <button className="p-1.5 rounded border border-glass-border bg-void text-text-secondary hover:text-text-primary hover:border-text-muted transition-colors">
             <Share2 className="w-4 h-4" />
           </button>
           <button className="p-1.5 rounded border border-glass-border bg-void text-text-secondary hover:text-text-primary hover:border-text-muted transition-colors">
             <Maximize className="w-4 h-4" />
           </button>
        </div>
      </motion.div>
    </Panel>
  );
});
PreviewToolbarWidget.displayName = "PreviewToolbarWidget";
