"use client";

import React, { useEffect } from "react";
import { TriplePanelLayout } from "@/components/layout/templates/TriplePanelLayout";
import { WidgetRenderer } from "@/components/layout/WidgetRenderer";
import { RuntimeProvider } from "@/contexts/RuntimeContext";
import { initializeRuntimeWidgets } from "@/components/widgets/runtime";

if (typeof window !== "undefined") {
  initializeRuntimeWidgets();
}

export default function RuntimeObservatoryPage() {
  const breadcrumbs = [
    { label: "Runtime Observatory" }
  ];

  const leftPanel = (
    <div className="flex flex-col h-full bg-void">
      <WidgetRenderer widgetId="kernel-status" />
      <div className="border-t border-glass-border">
        <WidgetRenderer widgetId="worker-pool" />
      </div>
    </div>
  );

  const centerPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-1">
        <WidgetRenderer widgetId="workflow-graph" />
      </div>
      <div className="border-t border-glass-border h-64">
        <WidgetRenderer widgetId="execution-timeline" />
      </div>
      <div className="border-t border-glass-border h-64">
        <WidgetRenderer widgetId="live-logs" />
      </div>
    </div>
  );

  const rightPanel = (
    <div className="flex flex-col h-full bg-void">
      <WidgetRenderer widgetId="provider-router" />
      <div className="border-t border-glass-border flex-1">
        <WidgetRenderer widgetId="metrics" />
      </div>
    </div>
  );

  return (
    <RuntimeProvider>
      <TriplePanelLayout
        id="runtime-observatory-layout"
        title="Runtime"
        leftPanel={leftPanel}
        centerPanel={centerPanel}
        rightPanel={rightPanel}
        leftSize={20}
        centerSize={55}
        rightSize={25}
      />
    </RuntimeProvider>
  );
}
