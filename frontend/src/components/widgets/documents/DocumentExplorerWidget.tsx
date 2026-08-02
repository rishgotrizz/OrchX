"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { FileText, Bot, FileJson, Hash, ChevronRight, Info } from "lucide-react";

const SEMANTIC_COLLECTIONS = [
  { id: 'product', label: 'Product', description: 'Product Scope & Roadmap (PRDs, Roadmaps, User Stories)' },
  { id: 'engineering', label: 'Engineering', description: 'Architecture Blueprints & Infrastructure Specs' },
  { id: 'research', label: 'Research', description: 'Multi-Agent Latency Benchmarking & Research' },
  { id: 'ai', label: 'AI Intelligence', description: 'Autonomous Agent Prompt Templates & Decision Traces' },
  { id: 'outputs', label: 'Outputs', description: 'Generated Code, Schema Definitions & API Contracts' },
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
    if (collectionId === 'product') return documents.filter(d => d.tags?.includes('product') || d.id === 'doc-2');
    if (collectionId === 'engineering') return documents.filter(d => d.tags?.includes('engineering') || d.id === 'doc-1' || d.id === 'doc-3');
    if (collectionId === 'research') return documents.filter(d => d.tags?.includes('research') || d.id === 'doc-4');
    if (collectionId === 'ai') return documents.filter(d => d.tags?.includes('ai') || d.id === 'doc-5' || d.type === 'prompt');
    if (collectionId === 'outputs') return documents.filter(d => d.tags?.includes('outputs') || d.id === 'doc-6');
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
                <div className="flex items-center gap-1.5">
                  <span>{collection.label}</span>
                  <div className="relative group/collinfo inline-block">
                    <button type="button" className="p-0.5 text-text-muted hover:text-accent-primary transition-colors">
                      <Info className="w-3 h-3" />
                    </button>
                    <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 w-56 p-2 bg-surface border border-glass-border rounded-xl shadow-2xl text-[11px] text-text-secondary opacity-0 pointer-events-none group-hover/collinfo:opacity-100 transition-opacity z-50 normal-case tracking-normal font-normal">
                      <span className="font-semibold text-text-primary block mb-0.5">{collection.label} Vault</span>
                      {collection.description}
                    </div>
                  </div>
                </div>
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
                      <div className="flex items-center space-x-2 overflow-hidden flex-1 min-w-0">
                        <Hash className="w-3.5 h-3.5 opacity-50 shrink-0" />
                        <span className="truncate">{doc.title}</span>
                      </div>
                      
                      <div className="relative group/docinfo shrink-0 ml-2">
                        <button 
                          type="button" 
                          onClick={(e) => { e.stopPropagation(); openDocument(doc.id); }}
                          className="p-0.5 text-text-muted hover:text-accent-primary transition-colors"
                        >
                          <Info className="w-3 h-3 opacity-60 group-hover/docinfo:opacity-100" />
                        </button>
                        <div className="absolute right-0 top-full mt-1 w-60 p-2 bg-surface border border-glass-border rounded-xl shadow-2xl text-[11px] text-text-secondary opacity-0 pointer-events-none group-hover/docinfo:opacity-100 transition-opacity z-50">
                          <span className="font-semibold text-text-primary block mb-0.5">{doc.title}</span>
                          {doc.tags ? `Tags: ${doc.tags.join(', ')}` : 'Document specification'}
                        </div>
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
