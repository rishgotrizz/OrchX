import { LucideIcon } from "lucide-react";

export interface DocumentMetadata {
  id: string; // Unique ID for this metadata registration
  title: string;
  type: string; // e.g., 'prompt', 'markdown', 'workflow'
  mimeType: string;
  icon: LucideIcon;
  category: string;
  language?: string;
  editor: string; // preferred editor driver ID
  renderer?: string;
  toolbar: string[];
  permissions: string[];
  capabilities: string[];
  tags: string[];
  supportedViews: ('edit' | 'preview' | 'split')[];
}

const REGISTRY = new Map<string, DocumentMetadata>();

export function registerDocumentType(metadata: DocumentMetadata) {
  REGISTRY.set(metadata.type, metadata);
}

export function getDocumentMetadata(type: string) {
  return REGISTRY.get(type);
}

export function getAllDocumentMetadata() {
  return Array.from(REGISTRY.values());
}
