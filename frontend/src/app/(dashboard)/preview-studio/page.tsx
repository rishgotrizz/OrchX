"use client";

import React, { useEffect } from "react";
import { TriplePanelLayout } from "@/components/layout/templates/TriplePanelLayout";
import { WidgetRenderer } from "@/components/layout/WidgetRenderer";
import { PreviewProvider } from "@/contexts/PreviewContext";
import { initializePreviewWidgets } from "@/components/widgets/preview";
import { initializePreviewDrivers } from "@/components/preview/drivers";
import { PreviewCanvas } from "@/components/preview/PreviewCanvas";

if (typeof window !== "undefined") {
  initializePreviewWidgets();
  initializePreviewDrivers();
}

export default function PreviewStudioPage() {
  const breadcrumbs = [
    { label: "Preview Studio" }
  ];

  const leftPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-[0.6] overflow-y-auto">
        <WidgetRenderer widgetId="artifact-explorer" />
      </div>
      <div className="flex-[0.4] border-t border-glass-border overflow-y-auto">
        <WidgetRenderer widgetId="version-history" />
      </div>
    </div>
  );

  const centerPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="shrink-0 border-b border-glass-border">
        <WidgetRenderer widgetId="preview-toolbar" />
      </div>
      <div className="flex-1 relative overflow-hidden bg-void-elevated">
         <PreviewCanvas />
      </div>
      <div className="h-48 shrink-0 border-t border-glass-border">
        <WidgetRenderer widgetId="preview-console" />
      </div>
    </div>
  );

  const rightPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-[0.5] overflow-y-auto">
        <WidgetRenderer widgetId="properties-inspector" />
      </div>
      <div className="flex-[0.5] border-t border-glass-border overflow-y-auto">
        <WidgetRenderer widgetId="preview-statistics" />
      </div>
    </div>
  );

  return (
    <PreviewProvider>
      <TriplePanelLayout
        id="preview-studio-layout"
        title="Preview"
        leftPanel={leftPanel}
        centerPanel={centerPanel}
        rightPanel={rightPanel}
        leftSize={20}
        centerSize={60}
        rightSize={20}
      />
    </PreviewProvider>
  );
}
