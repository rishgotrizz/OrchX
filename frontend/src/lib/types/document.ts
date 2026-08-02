export interface OrchXDocument {
  id: string;
  title: string;
  type: string; // 'markdown', 'prompt', 'code', 'workflow', 'json', etc.
  mimeType: string;
  content: string;
  projectId: string;
  folderId: string | null;
  version: number;
  author: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

export interface DocumentTab {
  id: string; // usually matches document id
  documentId: string;
  isDirty: boolean;
  isPinned: boolean;
  scrollPosition: number;
}

export interface DocumentSession {
  projectId: string | null;
  folderId: string | null;
  activeTabId: string | null;
  tabs: DocumentTab[];
  splitMode: 'none' | 'horizontal' | 'vertical';
  splitSecondaryTabId: string | null;
}
