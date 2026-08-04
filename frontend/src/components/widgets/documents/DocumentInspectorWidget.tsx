"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { Sparkles, CheckCircle2, FileText, ArrowRight, Tag, User, Calendar, Workflow } from "lucide-react";
import Link from "next/link";

export const DocumentInspectorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, documents } = useDocumentsContext();
  const doc = documents.find(d => d.id === session.activeTabId);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (!doc) return <Panel id="doc-inspector" header="Document Metadata" className="h-full border-none !bg-transparent"><div className="p-4 text-xs text-text-muted">No document selected</div></Panel>;

  const snippetText = doc.content 
    ? doc.content.replace(/^#\s+.*$/m, '').trim().slice(0, 180) + '...' 
    : 'No content specified.';

  return (
    <Panel id="doc-inspector" ref={panelRef} header="Document Metadata" className="h-full border-none !bg-transparent">
      <div className="flex flex-col h-full overflow-y-auto px-4 py-2 space-y-6 pb-12">
        
        {/* Document Overview */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-accent-primary" />
            Document Overview
          </h3>
          <p className="text-xs text-text-secondary leading-relaxed bg-surface/50 p-3 rounded-lg border border-glass-border">
            {snippetText}
          </p>
        </section>

        {/* Document Details */}
        <section className="space-y-3">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Metadata Details</h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center p-2 bg-void/50 rounded-lg border border-glass-border">
              <span className="text-text-muted flex items-center gap-1.5"><FileText className="w-3.5 h-3.5" /> Type:</span>
              <span className="font-mono text-text-primary uppercase">{doc.type || 'specification'}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-void/50 rounded-lg border border-glass-border">
              <span className="text-text-muted flex items-center gap-1.5"><User className="w-3.5 h-3.5" /> Author:</span>
              <span className="font-mono text-text-primary">{doc.author || 'User'}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-void/50 rounded-lg border border-glass-border">
              <span className="text-text-muted flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" /> Created:</span>
              <span className="font-mono text-text-primary">{doc.createdAt ? new Date(doc.createdAt).toLocaleDateString() : 'Today'}</span>
            </div>
          </div>
        </section>

        {/* Workflow Action */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-status-success uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Workflow Integration
          </h3>
          <div className="flex flex-col space-y-2">
            <Link 
              href={`/workflow-forge?mission=${encodeURIComponent(doc.title)}`}
              className="flex items-center justify-between text-left px-3 py-2 bg-accent-primary/10 border border-accent-primary/30 rounded-lg text-xs font-medium text-accent-primary hover:bg-accent-primary/20 transition-colors"
            >
              <span className="flex items-center gap-1.5"><Workflow className="w-3.5 h-3.5" /> Execute Workflow for {doc.title}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </section>

        {/* Document Tags */}
        {doc.tags && doc.tags.length > 0 && (
          <section className="space-y-2">
            <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-text-muted" /> Tags
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {doc.tags.map(tag => (
                <span key={tag} className="px-2 py-0.5 bg-surface border border-glass-border rounded-full text-[11px] text-text-secondary font-mono">
                  {tag}
                </span>
              ))}
            </div>
          </section>
        )}

      </div>
    </Panel>
  );
});
DocumentInspectorWidget.displayName = "DocumentInspectorWidget";
