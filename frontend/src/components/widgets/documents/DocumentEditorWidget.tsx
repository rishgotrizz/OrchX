"use client";

import React, { useRef, useImperativeHandle, forwardRef, useState } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { getEditorForType } from "@/lib/editor-registry";
import { Sparkles, ArrowRight, MessageSquare, Plus, ChevronDown } from "lucide-react";

const ProjectSnapshot = ({ doc }: { doc: any }) => (
  <div className="flex flex-col space-y-4 pb-8 mb-8 border-b border-glass-divider">
    <div className="flex items-start justify-between">
      <div className="flex flex-col space-y-1">
        <h1 className="text-3xl font-light text-text-primary">{doc.title}</h1>
        <div className="flex items-center space-x-3 text-sm text-text-secondary">
          <span className="px-2 py-0.5 bg-surface-hover rounded text-xs font-medium tracking-wider uppercase text-text-muted">Version 7</span>
          <span>•</span>
          <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-status-success" /> Review</span>
          <span>•</span>
          <span className="font-medium text-text-primary">82% Complete</span>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <button className="flex items-center gap-2 px-3 py-1.5 bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 transition-colors rounded-full text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>AI Actions</span>
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <div className="flex items-center space-x-4 text-sm bg-surface/50 p-3 rounded-lg border border-glass-border">
      <span className="text-text-muted font-medium uppercase text-xs tracking-wider">Ready For</span>
      <div className="flex items-center gap-2 text-text-primary">
        <span>Task Generation</span>
        <ArrowRight className="w-4 h-4 text-accent-primary" />
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
        <div className="flex items-center justify-center h-full text-text-muted">
           No project selected.
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

      {/* PRD Chat Drawer (Mock) */}
      {chatOpen && (
        <div className="absolute top-0 right-0 w-80 h-full bg-surface border-l border-glass-border shadow-2xl flex flex-col z-20">
          <div className="flex items-center justify-between p-4 border-b border-glass-border">
            <h3 className="text-sm font-medium flex items-center gap-2"><Sparkles className="w-4 h-4 text-accent-primary"/> PRD Chat</h3>
            <button onClick={() => setChatOpen(false)} className="text-text-muted hover:text-text-primary"><Plus className="w-4 h-4 rotate-45" /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 text-sm">
            <div className="bg-void p-3 rounded-lg text-text-secondary self-start max-w-[85%] border border-glass-divider">
              I can help you review this PRD. What would you like to know?
            </div>
          </div>
          <div className="p-4 border-t border-glass-border bg-void/50">
            <input type="text" placeholder="Ask about this PRD..." className="w-full bg-surface border border-glass-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-accent-primary text-text-primary placeholder:text-text-muted" />
          </div>
        </div>
      )}
    </Panel>
  );
});
DocumentEditorWidget.displayName = "DocumentEditorWidget";
