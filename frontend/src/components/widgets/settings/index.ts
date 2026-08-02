import { registerWidget } from "@/lib/widget-registry";
import { Settings, Sliders, Box, Network, Palette, Activity } from "lucide-react";
import { SettingsNavigationWidget } from "./SettingsNavigationWidget";
import { SettingsEditorWidget } from "./SettingsEditorWidget";
import { ProviderManagerWidget } from "./ProviderManagerWidget";
import { ModelManagerWidget } from "./ModelManagerWidget";
import { ThemeManagerWidget } from "./ThemeManagerWidget";
import { SettingsDiagnosticsWidget } from "./SettingsDiagnosticsWidget";
import { registerSettingsCategory, registerConfiguration } from "@/lib/settings-registry";
import { registerProvider } from "@/lib/provider-registry";
import { z } from "zod";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read", "write"],
  permissions: ["settings"],
  refreshPolicy: "event" as const,
  category: "settings",
};

export function initializeSettingsWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-navigation", title: "Navigation", description: "Categories", icon: Settings, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: SettingsNavigationWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-editor", title: "Preferences", description: "Form Editor", icon: Sliders, defaultSize: 60, minSize: 40, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: SettingsEditorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "provider-manager", title: "Providers", description: "API Status", icon: Box, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ProviderManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "model-manager", title: "Models", description: "Models List", icon: Network, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ModelManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "theme-manager", title: "Live Preview", description: "Appearance", icon: Palette, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ThemeManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-diagnostics", title: "Diagnostics", description: "Health", icon: Activity, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "medium", supportedLayouts: ["all"], component: SettingsDiagnosticsWidget });
}

export function initializeSettingsMockData() {
  registerSettingsCategory({ id: 'appearance', title: 'Appearance', icon: Palette, priority: 100 });
  registerSettingsCategory({ id: 'editor', title: 'Editor', icon: Sliders, priority: 90 });
  registerSettingsCategory({ id: 'workspace', title: 'Workspace', icon: Box, priority: 80 });

  registerConfiguration({
    id: 'appearance.theme',
    label: 'Theme Mode',
    description: 'Select the color theme for the UI.',
    category: 'appearance',
    type: 'select',
    defaultValue: 'dark',
    options: [{ label: 'Dark', value: 'dark' }, { label: 'Light', value: 'light' }],
    searchKeywords: ['theme', 'dark mode', 'color'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'appearance.density',
    label: 'UI Density',
    description: 'Control the spacing and sizing of UI elements.',
    category: 'appearance',
    type: 'select',
    defaultValue: 'comfortable',
    options: [{ label: 'Compact', value: 'compact' }, { label: 'Comfortable', value: 'comfortable' }, { label: 'Spacious', value: 'spacious' }],
    searchKeywords: ['density', 'spacing', 'size'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'editor.autoSave',
    label: 'Auto Save',
    description: 'Automatically save documents after a delay.',
    category: 'editor',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['save', 'auto', 'editor'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerProvider({
    id: 'openrouter',
    name: 'OpenRouter',
    status: 'connected',
    latencyMs: 145,
    health: 'healthy',
    capabilities: ['chat', 'completion'],
    models: [
      { id: 'gpt-4o', name: 'GPT-4o', providerId: 'openrouter', contextLength: 128000, capabilities: ['vision'] },
      { id: 'claude-3.5', name: 'Claude 3.5 Sonnet', providerId: 'openrouter', contextLength: 200000, capabilities: ['coding'] }
    ]
  });

  registerProvider({
    id: 'groq',
    name: 'Groq',
    status: 'connected',
    latencyMs: 12,
    health: 'healthy',
    capabilities: ['chat'],
    models: [
      { id: 'llama3-70b', name: 'Llama 3 70B', providerId: 'groq', contextLength: 8000, capabilities: ['fast'] }
    ]
  });
}
