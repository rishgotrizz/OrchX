import React from "react";

export interface PreviewDriver {
  id: string;
  name: string;
  supportedMimeTypes: string[];
  component: React.ComponentType<any>;
}

const REGISTRY = new Map<string, PreviewDriver>();

export function registerRenderer(driver: PreviewDriver) {
  REGISTRY.set(driver.id, driver);
}

export function getRenderer(id: string) {
  return REGISTRY.get(id);
}

export function getRendererForMimeType(mimeType: string) {
  return Array.from(REGISTRY.values()).find(d => d.supportedMimeTypes.includes(mimeType));
}
