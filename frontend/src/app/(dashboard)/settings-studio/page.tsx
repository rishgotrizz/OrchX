"use client";

import React from "react";
import { DualPanelLayout } from "@/components/layout/templates/DualPanelLayout";
import { WidgetRenderer } from "@/components/layout/WidgetRenderer";

// Registry initialization is handled globally in providers.tsx.
// No local initializeSettingsWidgets/initializeSettingsMockData call needed here.

export default function SettingsStudioPage() {
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
    <DualPanelLayout
      id="settings-studio-layout"
      title="Settings"
      leftPanel={leftPanel}
      rightPanel={rightPanel}
      leftSize={25}
      rightSize={75}
    />
  );
}
