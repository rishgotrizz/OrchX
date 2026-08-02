import React from "react";

export interface EditorDriver {
  id: string;
  name: string;
  supportedTypes: string[];
  component: React.ComponentType<any>;
}

const REGISTRY = new Map<string, EditorDriver>();

export function registerEditor(driver: EditorDriver) {
  REGISTRY.set(driver.id, driver);
}

export function getEditor(id: string) {
  return REGISTRY.get(id);
}

export function getEditorForType(type: string) {
  return Array.from(REGISTRY.values()).find(e => e.supportedTypes.includes(type));
}
