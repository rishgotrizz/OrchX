import { LucideIcon } from "lucide-react";
import React from "react";

export interface WidgetManifest {
  id: string;
  title: string;
  version: string;
  author: string;
  description: string;
  icon: LucideIcon;
  category: string;
  priority: 'high' | 'medium' | 'low';
  preferredLayout: 'horizontal' | 'vertical' | 'grid';
  supportedLayouts: string[];
  permissions: string[];
  capabilities: string[];
  dependencies?: string[];
  refreshPolicy: 'manual' | 'interval' | 'event' | 'stream';
  tags?: string[];
  homepage?: string;
  license?: string;
  minimumKernelVersion?: string;
  defaultSize: number; // Percentage
  minSize: number;
  component: React.ComponentType<any>;
}

const REGISTRY = new Map<string, WidgetManifest>();

export function registerWidget(manifest: WidgetManifest) {
  REGISTRY.set(manifest.id, manifest);
}

export function getWidget(id: string): WidgetManifest | undefined {
  return REGISTRY.get(id);
}

export function getAllWidgets(): WidgetManifest[] {
  return Array.from(REGISTRY.values());
}
