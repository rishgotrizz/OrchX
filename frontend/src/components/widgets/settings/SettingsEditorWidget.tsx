"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useSettingsContext } from "@/contexts/SettingsContext";
import { getConfigurationsByCategory, searchConfigurations } from "@/lib/settings-registry";
import { useForm, Controller } from "react-hook-form";

export const SettingsEditorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, getSettingValue, updateSettingValue } = useSettingsContext();
  
  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const configs = session.searchQuery 
    ? searchConfigurations(session.searchQuery)
    : getConfigurationsByCategory(session.currentCategory);

  const { control } = useForm();

  return (
    <Panel id="settings-editor" ref={panelRef} header="Preferences" className="h-full border border-glass-border shadow-glow">
      <div className="flex flex-col space-y-6 h-full overflow-y-auto p-2">
        {configs.length === 0 && <div className="text-text-muted text-sm">No settings found.</div>}
        {configs.map(config => {
          const value = getSettingValue(config.id);
          return (
            <div key={config.id} className="flex flex-col space-y-2">
              <div className="flex flex-col">
                <span className="text-sm font-medium text-text-primary">{config.label}</span>
                <span className="text-xs text-text-muted">{config.description}</span>
              </div>
              <div className="mt-1">
                {config.type === 'boolean' && (
                  <Controller
                    control={control}
                    name={config.id}
                    defaultValue={value}
                    render={({ field }) => (
                      <input 
                        type="checkbox" 
                        checked={field.value} 
                        onChange={(e) => {
                          field.onChange(e.target.checked);
                          updateSettingValue(config.id, e.target.checked, true);
                        }} 
                        className="w-4 h-4 text-accent-primary bg-surface border-glass-border rounded focus:ring-accent-primary focus:ring-2"
                      />
                    )}
                  />
                )}
                {config.type === 'string' && !config.options && (
                  <Controller
                    control={control}
                    name={config.id}
                    defaultValue={value}
                    render={({ field }) => (
                      <input 
                        type="text" 
                        value={field.value} 
                        onChange={(e) => {
                          field.onChange(e.target.value);
                          updateSettingValue(config.id, e.target.value, true);
                        }}
                        className="w-full max-w-md bg-surface border border-glass-border rounded px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
                      />
                    )}
                  />
                )}
                {config.type === 'select' && config.options && (
                  <Controller
                    control={control}
                    name={config.id}
                    defaultValue={value}
                    render={({ field }) => (
                      <select 
                        value={field.value} 
                        onChange={(e) => {
                          field.onChange(e.target.value);
                          updateSettingValue(config.id, e.target.value, true);
                        }}
                        className="w-full max-w-md bg-surface border border-glass-border rounded px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
                      >
                        {config.options!.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                      </select>
                    )}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
});
SettingsEditorWidget.displayName = "SettingsEditorWidget";
