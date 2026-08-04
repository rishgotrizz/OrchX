"use client";

import React, { useRef, useImperativeHandle, forwardRef, useState } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { getEditorForType } from "@/lib/editor-registry";
import { Sparkles, ArrowRight, MessageSquare, Plus, ChevronDown } from "lucide-react";

const ProjectSnapshot = ({ doc }: { doc: any }) => (
  <div className="flex flex-col space-y-4 pb-6 mb-6 border-b border-glass-divider">
    <div className="flex items-start justify-between">
      <div className="flex flex-col space-y-1">
        <h1 className="text-3xl font-light text-text-primary">{doc.title}</h1>
        <div className="flex items-center space-x-3 text-xs text-text-secondary">
          <span className="px-2 py-0.5 bg-surface-hover rounded text-xs font-medium tracking-wider uppercase text-text-muted">
            Version {doc.version || 1}
          </span>
          <span>•</span>
          <span className="flex items-center gap-1.5 font-mono text-status-success">
            <div className="w-1.5 h-1.5 rounded-full bg-status-success" /> 
            {doc.status || 'Active'}
          </span>
          <span>•</span>
          <span className="font-mono text-text-muted">
            Updated: {doc.updatedAt ? new Date(doc.updatedAt).toLocaleDateString() : 'Today'}
          </span>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <button className="flex items-center gap-2 px-3 py-1.5 bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 transition-colors rounded-full text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Specification Active</span>
        </button>
      </div>
    </div>
  </div>
);

export const DocumentEditorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, documents } = useDocumentsContext();
  const [chatOpen, setChatOpen] = useState(false);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const activeDocument = documents.find(d => d.id === session.activeTabId);
  const activeEditorDef = activeDocument ? getEditorForType(activeDocument.type) : null;
  const ActiveEditorComponent = activeEditorDef?.component;

  if (!activeDocument) {
    return (
      <Panel id="document-editor" ref={panelRef} className="h-full !bg-void !p-0 overflow-hidden border-none !bg-transparent">
        <div className="flex flex-col items-center justify-center h-full text-text-muted space-y-4">
          <div className="p-4 rounded-full bg-surface border border-glass-border">
            <Sparkles className="w-8 h-8 text-accent-primary" />
          </div>
          <div className="flex flex-col items-center text-center space-y-1">
            <span className="text-lg font-bold text-text-primary">No Document Selected</span>
            <span className="text-xs text-text-secondary max-w-sm">Select an existing specification from the left collections or create a new custom document.</span>
          </div>
        </div>
      </Panel>
    );
  }

  return (
    <Panel id="document-editor" ref={panelRef} className="h-full !bg-void !p-0 overflow-hidden relative border-none !bg-transparent">
      <div className="flex-1 bg-void overflow-y-auto h-full px-12 py-16 scroll-smooth">
        <div className="max-w-4xl mx-auto">
          <ProjectSnapshot doc={activeDocument} />
          
          <div className="prose prose-invert prose-p:text-text-secondary prose-headings:font-medium prose-a:text-accent-primary max-w-none">
            {ActiveEditorComponent ? (
              <ActiveEditorComponent document={activeDocument} />
            ) : (
              <div className="text-text-muted">Editor unavailable.</div>
            )}
          </div>
        </div>
      </div>
      
      {/* Ask AI Floating Button */}
      <button 
        onClick={() => setChatOpen(!chatOpen)}
        className="absolute bottom-8 right-8 flex items-center justify-center w-12 h-12 bg-surface border border-glass-border shadow-glow rounded-full text-text-secondary hover:text-accent-primary hover:border-accent-primary/50 transition-all z-10"
      >
        <MessageSquare className="w-5 h-5" />
      </button>

      {/* PRD Chat Drawer */}
      {chatOpen && (
        <div className="absolute top-0 right-0 w-80 h-full bg-surface border-l border-glass-border shadow-2xl flex flex-col z-20">
          <div className="flex items-center justify-between p-4 border-b border-glass-border">
            <h3 className="text-sm font-medium flex items-center gap-2"><Sparkles className="w-4 h-4 text-accent-primary"/> Assistant</h3>
            <button onClick={() => setChatOpen(false)} className="text-text-muted hover:text-text-primary"><Plus className="w-4 h-4 rotate-45" /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 text-sm">
            <div className="bg-void p-3 rounded-lg text-text-secondary self-start max-w-[85%] border border-glass-divider text-xs">
              Reviewing specification for {activeDocument.title}...
            </div>
          </div>
          <div className="p-4 border-t border-glass-border bg-void/50">
            <input type="text" placeholder="Ask about this document..." className="w-full bg-surface border border-glass-border rounded-md px-3 py-2 text-xs focus:outline-none focus:border-accent-primary text-text-primary placeholder:text-text-muted" />
          </div>
        </div>
      )}
    </Panel>
  );
});
DocumentEditorWidget.displayName = "DocumentEditorWidget";
