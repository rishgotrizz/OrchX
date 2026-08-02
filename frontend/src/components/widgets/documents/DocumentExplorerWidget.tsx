"use client";

import React, { useRef, useImperativeHandle, forwardRef, useState } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { FileText, Bot, FileJson, Hash, ChevronRight, Info, Plus, Trash2, Check, X } from "lucide-react";

const SEMANTIC_COLLECTIONS = [
  { id: 'product', label: 'Product', description: 'Product Scope & Roadmap (PRDs, Roadmaps, User Stories)' },
  { id: 'engineering', label: 'Engineering', description: 'Architecture Blueprints & Infrastructure Specs' },
  { id: 'research', label: 'Research', description: 'Multi-Agent Latency Benchmarking & Research' },
  { id: 'ai', label: 'AI Intelligence', description: 'Autonomous Agent Prompt Templates & Decision Traces' },
  { id: 'outputs', label: 'Outputs', description: 'Generated Code, Schema Definitions & API Contracts' },
];

export const DocumentExplorerWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { documents, session, setSession, createDocument, deleteDocument } = useDocumentsContext();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("product");

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
    return documents.filter(d => 
      d.tags?.includes(collectionId) || 
      (collectionId === 'product' && (d.tags?.includes('product') || d.id === 'doc-2')) ||
      (collectionId === 'engineering' && (d.tags?.includes('engineering') || d.id === 'doc-1' || d.id === 'doc-3')) ||
      (collectionId === 'research' && (d.tags?.includes('research') || d.id === 'doc-4')) ||
      (collectionId === 'ai' && (d.tags?.includes('ai') || d.id === 'doc-5')) ||
      (collectionId === 'outputs' && (d.tags?.includes('outputs') || d.id === 'doc-6'))
    );
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    createDocument(newTitle, selectedCategory);
    setNewTitle("");
    setIsModalOpen(false);
  };

  return (
    <Panel id="doc-explorer" ref={panelRef} header="Collections" className="h-full border-none !bg-transparent">
      <div className="flex flex-col h-full overflow-y-auto px-4 py-2 space-y-5">
        
        {/* Top Header & Create Document Trigger */}
        <div className="flex items-center justify-between border-b border-glass-divider pb-3">
          <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Document Vault</span>
          <button
            onClick={() => { setSelectedCategory("product"); setIsModalOpen(true); }}
            className="flex items-center space-x-1.5 px-2.5 py-1 bg-accent-primary hover:bg-accent-hover text-white rounded-lg text-xs font-medium transition-colors shadow-glow"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Document</span>
          </button>
        </div>

        {/* Inline Modal Form for Document Creation */}
        {isModalOpen && (
          <form onSubmit={handleCreateSubmit} className="p-3 bg-surface border border-glass-border rounded-xl flex flex-col space-y-3 shadow-2xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-accent-primary uppercase tracking-wider">Create Specification</span>
              <button type="button" onClick={() => setIsModalOpen(false)} className="text-text-muted hover:text-text-primary text-xs">✕</button>
            </div>
            <input
              type="text"
              placeholder="Document Title (e.g. System Blueprint)"
              value={newTitle}
              onChange={e => setNewTitle(e.target.value)}
              className="w-full bg-void border border-glass-border rounded-lg px-3 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent-primary"
              autoFocus
            />
            <div className="flex items-center space-x-2">
              <select
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
                className="flex-1 bg-void border border-glass-border rounded-lg px-2.5 py-1 text-xs text-text-primary focus:outline-none focus:border-accent-primary"
              >
                {SEMANTIC_COLLECTIONS.map(c => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
              <button
                type="submit"
                className="px-3 py-1 bg-accent-primary hover:bg-accent-hover text-white rounded-lg text-xs font-medium transition-colors"
              >
                Create
              </button>
            </div>
          </form>
        )}

        {/* Collections List */}
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
                
                <div className="flex items-center space-x-1.5">
                  <button
                    onClick={() => { setSelectedCategory(collection.id); setIsModalOpen(true); }}
                    className="p-0.5 text-text-muted hover:text-accent-primary transition-colors"
                    title={`Add document to ${collection.label}`}
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                  <span className="bg-surface px-1.5 py-0.5 rounded-full text-[10px]">{docs.length}</span>
                </div>
              </div>
              
              <div className="flex flex-col space-y-0.5">
                {docs.length === 0 ? (
                  <div 
                    onClick={() => { setSelectedCategory(collection.id); setIsModalOpen(true); }}
                    className="text-xs text-text-muted/50 italic px-2 py-1.5 border border-dashed border-glass-border rounded-md hover:border-accent-primary/50 hover:text-accent-primary cursor-pointer transition-colors flex items-center space-x-1.5"
                  >
                    <Plus className="w-3 h-3" />
                    <span>Create {collection.label} document...</span>
                  </div>
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
                      
                      <div className="flex items-center space-x-1 shrink-0 ml-2">
                        {doc.id.startsWith('doc-user-') && (
                          <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }}
                            className="p-0.5 text-text-muted hover:text-status-error opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Delete Document"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        )}
                        <div className="relative group/docinfo">
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
