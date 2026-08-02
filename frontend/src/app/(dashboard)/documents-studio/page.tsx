"use client";

import React, { useEffect } from "react";
import { TriplePanelLayout } from "@/components/layout/templates/TriplePanelLayout";
import { WidgetRenderer } from "@/components/layout/WidgetRenderer";
import { DocumentsProvider } from "@/contexts/DocumentsContext";
import { initializeDocumentWidgets } from "@/components/widgets/documents";
import { initializeDocumentEditors } from "@/components/documents/editors";

if (typeof window !== "undefined") {
  initializeDocumentWidgets();
  initializeDocumentEditors();
}

export default function DocumentsStudioPage() {
  const breadcrumbs = [
    { label: "Documents Studio" }
  ];

  const leftPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="shrink-0 border-b border-glass-border">
        <WidgetRenderer widgetId="global-search" />
      </div>
      <div className="flex-1 overflow-y-auto">
        <WidgetRenderer widgetId="doc-explorer" />
      </div>
    </div>
  );

  const centerPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-1 overflow-hidden">
        <WidgetRenderer widgetId="doc-editor" />
      </div>
    </div>
  );

  const rightPanel = (
    <div className="flex flex-col h-full bg-void">
      <div className="flex-1 overflow-y-auto">
        <WidgetRenderer widgetId="doc-inspector" />
      </div>
    </div>
  );

  return (
    <DocumentsProvider>
      <TriplePanelLayout
        id="documents-studio-layout"
        title="Projects"
        leftPanel={leftPanel}
        centerPanel={centerPanel}
        rightPanel={rightPanel}
        leftSize={15}
        centerSize={65}
        rightSize={20}
      />
    </DocumentsProvider>
  );
}
