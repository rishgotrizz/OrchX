"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { Plus, Save, Copy, Share2, Download, SplitSquareHorizontal } from "lucide-react";

export const DocumentToolbarWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const actions = [
    { icon: Plus, label: 'New' },
    { icon: Save, label: 'Save' },
    { icon: Copy, label: 'Duplicate' },
    { icon: SplitSquareHorizontal, label: 'Split' },
    { icon: Share2, label: 'Share' },
    { icon: Download, label: 'Export' },
  ];

  return (
    <Panel id="doc-toolbar" ref={panelRef} className="h-full !bg-surface/50 border border-glass-border">
      <div className="flex items-center space-x-1 h-full px-2">
        {actions.map(action => (
          <button key={action.label} className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded transition-colors" title={action.label}>
            <action.icon className="w-4 h-4" />
          </button>
        ))}
      </div>
    </Panel>
  );
});
DocumentToolbarWidget.displayName = "DocumentToolbarWidget";
