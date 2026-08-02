"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";

// Wait, I should import from SettingsContext
import { useSettingsContext as useActualSettingsContext } from "@/contexts/SettingsContext";
import { getCategories } from "@/lib/settings-registry";
import { Search } from "lucide-react";

export const SettingsNavigationWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, setSession } = useActualSettingsContext();
  const categories = getCategories();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  return (
    <Panel id="settings-navigation" ref={panelRef} header="Navigation" className="h-full">
      <div className="flex flex-col h-full space-y-4">
        <div className="relative shrink-0">
          <Search className="absolute left-2 top-1.5 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search settings..."
            value={session.searchQuery}
            onChange={e => setSession(s => ({ ...s, searchQuery: e.target.value }))}
            className="w-full bg-surface border border-glass-border rounded pl-8 pr-2 py-1 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
          />
        </div>
        <div className="flex-1 overflow-y-auto space-y-1">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSession(s => ({ ...s, currentCategory: cat.id }))}
              className={`flex items-center space-x-2 w-full px-2 py-1.5 text-sm rounded transition-colors text-left ${session.currentCategory === cat.id ? 'bg-accent-primary/10 text-accent-primary font-medium' : 'text-text-primary hover:bg-surface-hover'}`}
            >
              <cat.icon className="w-4 h-4" />
              <span>{cat.title}</span>
            </button>
          ))}
        </div>
      </div>
    </Panel>
  );
});
SettingsNavigationWidget.displayName = "SettingsNavigationWidget";
