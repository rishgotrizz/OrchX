"use client";

import React, { useEffect } from "react";
import { DualPanelLayout } from "@/components/layout/templates/DualPanelLayout";
import { WidgetRenderer } from "@/components/layout/WidgetRenderer";
import { SettingsProvider } from "@/contexts/SettingsContext";
import { initializeSettingsWidgets, initializeSettingsMockData } from "@/components/widgets/settings";

if (typeof window !== "undefined") {
  initializeSettingsWidgets();
  initializeSettingsMockData();
}

export default function SettingsStudioPage() {
  const breadcrumbs = [
    { label: "Settings Studio" }
  ];

  const leftPanel = (
    <div className="flex flex-col h-full bg-void border-r border-glass-border">
      <div className="flex-1 overflow-y-auto">
        <WidgetRenderer widgetId="settings-navigation" />
      </div>
    </div>
  );

  const rightPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-[0.5] border-b border-glass-border overflow-y-auto">
        <WidgetRenderer widgetId="settings-editor" />
      </div>
      <div className="flex-[0.5] flex overflow-y-auto">
        <div className="flex-1 border-r border-glass-border">
          <WidgetRenderer widgetId="provider-manager" />
        </div>
        <div className="flex-1">
          <WidgetRenderer widgetId="model-manager" />
        </div>
      </div>
    </div>
  );

  return (
    <SettingsProvider>
      <DualPanelLayout
        id="settings-studio-layout"
        title="Settings"
        leftPanel={leftPanel}
        rightPanel={rightPanel}
        leftSize={25}
        rightSize={75}
      />
    </SettingsProvider>
  );
}
