"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { Sparkles, FileText, Code } from "lucide-react";

export const AISuggestionsWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const suggestions = [
    { label: 'Rewrite for clarity', icon: FileText },
    { label: 'Generate unit tests', icon: Code },
    { label: 'Summarize document', icon: Sparkles },
  ];

  return (
    <Panel id="ai-suggestions" ref={panelRef} header="AI Suggestions" className="h-full">
      <div className="flex flex-col space-y-2">
        {suggestions.map(s => (
          <button key={s.label} className="flex items-center space-x-2 w-full p-2 text-xs bg-void hover:bg-surface border border-glass-border rounded transition-colors text-left text-text-primary group">
            <s.icon className="w-3.5 h-3.5 text-accent-primary group-hover:scale-110 transition-transform" />
            <span>{s.label}</span>
          </button>
        ))}
      </div>
    </Panel>
  );
});
AISuggestionsWidget.displayName = "AISuggestionsWidget";
