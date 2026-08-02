"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { useDocumentsContext } from "@/contexts/DocumentsContext";
import { Sparkles, CheckCircle2, AlertTriangle, FileText, ArrowRight } from "lucide-react";

const ProgressBar = ({ label, percentage }: { label: string, percentage: number }) => (
  <div className="flex flex-col space-y-1">
    <div className="flex justify-between text-xs">
      <span className="text-text-secondary">{label}</span>
      <span className="text-text-primary font-medium">{percentage}%</span>
    </div>
    <div className="h-1.5 w-full bg-surface-hover rounded-full overflow-hidden">
      <div 
        className="h-full bg-accent-primary rounded-full transition-all duration-500 ease-out" 
        style={{ width: `${percentage}%` }}
      />
    </div>
  </div>
);

export const DocumentInspectorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, documents } = useDocumentsContext();
  const doc = documents.find(d => d.id === session.activeTabId);

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (!doc) return <Panel id="doc-inspector" header="AI Intelligence" className="h-full border-none !bg-transparent"><div className="p-4 text-xs text-text-muted">No document selected</div></Panel>;

  return (
    <Panel id="doc-inspector" ref={panelRef} header="AI Intelligence" className="h-full border-none !bg-transparent">
      <div className="flex flex-col h-full overflow-y-auto px-4 py-2 space-y-8 pb-12">
        
        {/* Executive Summary */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-accent-primary" />
            Executive Summary
          </h3>
          <p className="text-sm text-text-secondary leading-relaxed">
            The CRM SaaS is a scalable platform designed to unify customer interactions. The MVP focuses on contact management, deal tracking, and basic reporting, with AI-driven insights planned for Phase 2.
          </p>
        </section>

        {/* Project Health */}
        <section className="space-y-4">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Project Health</h3>
          <div className="space-y-3">
            <ProgressBar label="Requirements" percentage={90} />
            <ProgressBar label="Architecture" percentage={75} />
            <ProgressBar label="Database" percentage={82} />
            <ProgressBar label="Testing" percentage={45} />
          </div>
        </section>

        {/* Missing Requirements */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-status-warning uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            Missing Requirements
          </h3>
          <div className="flex flex-col space-y-1">
            <div className="text-sm text-text-secondary flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-status-warning" /> Missing 3 User Stories for Analytics</div>
            <div className="text-sm text-text-secondary flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-status-warning" /> Stripe Webhook API undefined</div>
            <div className="text-sm text-text-secondary flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-status-warning" /> Team Roles schema missing</div>
          </div>
        </section>

        {/* Next Steps */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-status-success uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Recommended Next Steps
          </h3>
          <div className="flex flex-col space-y-2">
            <button className="flex items-center justify-between text-left px-3 py-2 bg-surface-hover rounded-md text-sm text-text-primary hover:bg-surface-active transition-colors">
              <span>Approve Requirements</span>
              <ArrowRight className="w-3.5 h-3.5 text-text-muted" />
            </button>
            <button className="flex items-center justify-between text-left px-3 py-2 bg-surface-hover rounded-md text-sm text-text-primary hover:bg-surface-active transition-colors">
              <span>Generate API Specification</span>
              <ArrowRight className="w-3.5 h-3.5 text-text-muted" />
            </button>
          </div>
        </section>

        {/* Project Context */}
        <section className="space-y-2">
          <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">Project Context</h3>
          <div className="flex flex-wrap gap-1.5">
            {['Next.js', 'PostgreSQL', 'Stripe', 'B2B SaaS', 'Multi-tenant'].map(tag => (
              <span key={tag} className="px-2 py-1 bg-surface border border-glass-border rounded-full text-xs text-text-secondary">
                {tag}
              </span>
            ))}
          </div>
        </section>

      </div>
    </Panel>
  );
});
DocumentInspectorWidget.displayName = "DocumentInspectorWidget";
