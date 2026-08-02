import { LucideIcon } from "lucide-react";

export interface ArtifactMetadata {
  id: string;
  name: string;
  version: string;
  category: string;
  supportedMimeTypes: string[];
  icon: LucideIcon;
  renderer: string; // ID of the default renderer
  toolbar: string[]; // List of default toolbar action IDs
  capabilities: string[];
  priority: number;
  supportedViews: ('preview' | 'source' | 'split')[];
  permissions: string[];
  tags: string[];
}

const REGISTRY = new Map<string, ArtifactMetadata>();

export function registerArtifact(metadata: ArtifactMetadata) {
  REGISTRY.set(metadata.id, metadata);
}

export function getArtifactMetadata(id: string) {
  return REGISTRY.get(id);
}

export function getAllArtifactMetadata() {
  return Array.from(REGISTRY.values());
}
