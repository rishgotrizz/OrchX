"use client";

import React, { useRef, useImperativeHandle, forwardRef, useState } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { Search, FileText } from "lucide-react";

export const GlobalSearchWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { documents, setSession } = useDocumentsContext();
  const [query, setQuery] = useState("");

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const results = query ? documents.filter(d => d.title.toLowerCase().includes(query.toLowerCase()) || d.content.toLowerCase().includes(query.toLowerCase())) : [];

  return (
    <Panel id="global-search" ref={panelRef} header="Search" className="h-full">
      <div className="flex flex-col h-full">
        <div className="relative mb-2 shrink-0">
          <Search className="absolute left-2 top-1.5 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search documents..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-full bg-surface border border-glass-border rounded pl-8 pr-2 py-1 text-sm text-text-primary focus:outline-none focus:border-accent-primary"
          />
        </div>
        <div className="flex-1 overflow-y-auto space-y-1">
          {results.map(doc => (
            <div 
              key={doc.id} 
              onClick={() => setSession(s => {
                const exists = s.tabs.find(t => t.documentId === doc.id);
                if (exists) return { ...s, activeTabId: doc.id };
                return { ...s, activeTabId: doc.id, tabs: [...s.tabs, { id: doc.id, documentId: doc.id, isDirty: false, isPinned: false, scrollPosition: 0 }] };
              })}
              className="flex items-center space-x-2 p-1.5 hover:bg-surface-hover rounded cursor-pointer border border-transparent hover:border-glass-border"
            >
              <FileText className="w-3.5 h-3.5 text-text-secondary" />
              <div className="flex flex-col">
                <span className="text-xs text-text-primary truncate">{doc.title}</span>
                <span className="text-[10px] text-text-muted truncate">{doc.projectId}</span>
              </div>
            </div>
          ))}
          {query && results.length === 0 && <span className="text-xs text-text-muted">No results found.</span>}
        </div>
      </div>
    </Panel>
  );
});
GlobalSearchWidget.displayName = "GlobalSearchWidget";
