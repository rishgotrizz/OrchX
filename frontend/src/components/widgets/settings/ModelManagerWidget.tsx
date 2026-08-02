"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useProviders } from "@/hooks/useProviders";
import { Network, Zap } from "lucide-react";

export const ModelManagerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const { providers, isLoading } = useProviders();
  const models = providers.flatMap(p => p.models);

  if (isLoading) return <Panel id="model-manager" header="Models" className="h-full"><div className="p-4 text-sm text-text-muted">Loading models...</div></Panel>;
  if (models.length === 0) return <Panel id="model-manager" header="Models" className="h-full"><div/></Panel>;

  return (
    <Panel id="model-manager" ref={panelRef} header="Models" className="h-full">
      <div className="flex flex-col space-y-2 h-full overflow-y-auto">
        {models.map(model => {
          const provider = providers.find(p => p.id === model.providerId);
          return (
            <div key={model.id} className="flex flex-col p-2 bg-surface hover:bg-surface-hover border border-glass-border rounded transition-colors cursor-pointer">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-text-primary">{model.name}</span>
                <Network className="w-3.5 h-3.5 text-accent-primary" />
              </div>
              <div className="flex items-center space-x-2 mt-1 text-xs text-text-muted">
                <span>{provider?.name}</span>
                <span>•</span>
                <span className="flex items-center space-x-1"><Zap className="w-3 h-3" /> <span>{(model.contextLength / 1000).toFixed(0)}k ctx</span></span>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
});
ModelManagerWidget.displayName = "ModelManagerWidget";
