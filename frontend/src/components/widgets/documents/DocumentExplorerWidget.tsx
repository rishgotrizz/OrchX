"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { FileText, Bot, FileJson, Hash, ChevronRight } from "lucide-react";

const SEMANTIC_COLLECTIONS = [
  { id: 'product', label: 'Product', description: 'PRDs, Roadmaps, User Stories' },
  { id: 'engineering', label: 'Engineering', description: 'Architecture, APIs, Database' },
  { id: 'research', label: 'Research', description: 'Notes, Competitor Analysis' },
  { id: 'ai', label: 'AI Intelligence', description: 'Conversations, Decisions, Reasoning' },
  { id: 'outputs', label: 'Outputs', description: 'Generated Reports, Code' },
];

export const DocumentExplorerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { documents, session, setSession } = useDocumentsContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const openDocument = (id: string) => {
    setSession(s => {
      const exists = s.tabs.find(t => t.documentId === id);
      if (exists) return { ...s, activeTabId: id };
      return { ...s, activeTabId: id, tabs: [...s.tabs, { id, documentId: id, isDirty: false, isPinned: false, scrollPosition: 0 }] };
    });
  };

  const getCollectionDocs = (collectionId: string) => {
    // Basic mock categorization based on document type or title
    if (collectionId === 'product') return documents.filter(d => d.type === 'markdown' && !d.title.includes('Architecture'));
    if (collectionId === 'engineering') return documents.filter(d => d.title.includes('Architecture') || d.type === 'workflow');
    if (collectionId === 'ai') return documents.filter(d => d.type === 'prompt');
    return [];
  };

  return (
    <Panel id="doc-explorer" ref={panelRef} header="Collections" className="h-full border-none !bg-transparent">
      <div className="flex flex-col h-full overflow-y-auto px-4 py-2 space-y-6">
        
        {SEMANTIC_COLLECTIONS.map(collection => {
          const docs = getCollectionDocs(collection.id);
          
          return (
            <div key={collection.id} className="flex flex-col space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-text-muted tracking-wider uppercase">
                <span>{collection.label}</span>
                <span className="bg-surface px-1.5 py-0.5 rounded-full text-[10px]">{docs.length}</span>
              </div>
              
              <div className="flex flex-col space-y-0.5">
                {docs.length === 0 ? (
                  <div className="text-xs text-text-muted/50 italic px-2 py-1">No documents</div>
                ) : (
                  docs.map(doc => (
                    <div
                      key={doc.id}
                      onClick={() => openDocument(doc.id)}
                      className={`group flex items-center justify-between px-2 py-1.5 text-sm rounded-md cursor-pointer transition-colors ${session.activeTabId === doc.id ? 'bg-accent-primary/10 text-accent-primary font-medium' : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}`}
                    >
                      <div className="flex items-center space-x-2 overflow-hidden">
                        <Hash className="w-3.5 h-3.5 opacity-50 shrink-0" />
                        <span className="truncate">{doc.title}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
});
DocumentExplorerWidget.displayName = "DocumentExplorerWidget";
