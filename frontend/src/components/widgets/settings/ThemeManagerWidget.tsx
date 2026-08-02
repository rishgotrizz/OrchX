"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useSettingsContext } from "@/contexts/SettingsContext";

export const ThemeManagerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { getSettingValue } = useSettingsContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const themeMode = getSettingValue('appearance.theme') || 'dark';
  const density = getSettingValue('appearance.density') || 'comfortable';

  return (
    <Panel id="theme-manager" ref={panelRef} header="Live Preview" className="h-full">
      <div className={`flex flex-col items-center justify-center h-full border-2 border-dashed border-glass-border rounded-lg ${themeMode === 'light' ? 'bg-white text-black' : 'bg-void text-white'}`}>
         <div className="text-sm font-medium mb-2">UI Component</div>
         <button className={`bg-accent-primary text-white rounded transition-all hover:opacity-90 ${density === 'compact' ? 'px-2 py-1 text-xs' : density === 'comfortable' ? 'px-4 py-2 text-sm' : 'px-6 py-3 text-base'}`}>
           Primary Button
         </button>
      </div>
    </Panel>
  );
});
ThemeManagerWidget.displayName = "ThemeManagerWidget";
