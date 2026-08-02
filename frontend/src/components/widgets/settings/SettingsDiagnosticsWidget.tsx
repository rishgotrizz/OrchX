"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";

export const SettingsDiagnosticsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  return (
    <Panel id="settings-diagnostics" ref={panelRef} header="Diagnostics" className="h-full">
      <div className="flex flex-col space-y-2 text-xs font-mono">
        <div className="flex justify-between text-text-primary"><span>Version</span><span className="text-accent-primary">v1.0.0-beta</span></div>
        <div className="flex justify-between text-text-primary"><span>Storage</span><span className="text-status-success">LocalStorage</span></div>
        <div className="flex justify-between text-text-primary"><span>Registries</span><span className="text-status-success">Loaded</span></div>
        <div className="flex justify-between text-text-primary"><span>Memory</span><span>120MB</span></div>
      </div>
    </Panel>
  );
});
SettingsDiagnosticsWidget.displayName = "SettingsDiagnosticsWidget";
