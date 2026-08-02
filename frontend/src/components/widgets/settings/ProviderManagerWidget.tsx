"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useProviders } from "@/hooks/useProviders";
import { Activity, Key, CheckCircle, XCircle } from "lucide-react";

export const ProviderManagerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const { providers, isLoading } = useProviders();
  if (isLoading) return <Panel id="provider-manager" header="Providers" className="h-full"><div className="p-4 text-sm text-text-muted">Loading providers...</div></Panel>;
  if (providers.length === 0) return <Panel id="provider-manager" header="Providers" className="h-full"><div/></Panel>;

  return (
    <Panel id="provider-manager" ref={panelRef} header="Providers" className="h-full">
      <div className="flex flex-col space-y-4 h-full overflow-y-auto">
        {providers.map(provider => (
          <div key={provider.id} className="flex flex-col p-3 bg-surface border border-glass-border rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-text-primary">{provider.name}</span>
              {provider.status === 'connected' ? <CheckCircle className="w-4 h-4 text-status-success" /> : <XCircle className="w-4 h-4 text-status-error" />}
            </div>
            <div className="flex items-center space-x-4 text-xs text-text-muted">
              <div className="flex items-center space-x-1"><Activity className="w-3 h-3" /><span>{provider.latencyMs}ms</span></div>
              <div className="flex items-center space-x-1"><Key className="w-3 h-3" /><span>Configured</span></div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
});
ProviderManagerWidget.displayName = "ProviderManagerWidget";
