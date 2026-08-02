import { LucideIcon } from "lucide-react";

export interface ToolbarAction {
  id: string;
  label: string;
  icon: LucideIcon;
  shortcut?: string;
  execute: (context: any) => void;
}

const REGISTRY = new Map<string, ToolbarAction>();

export function registerToolbarAction(action: ToolbarAction) {
  REGISTRY.set(action.id, action);
}

export function getToolbarAction(id: string) {
  return REGISTRY.get(id);
}

export function getAllToolbarActions() {
  return Array.from(REGISTRY.values());
}
