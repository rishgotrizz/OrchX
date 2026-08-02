"use client";

import React, { useRef, useImperativeHandle, forwardRef, useState } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { usePreviewContext } from "@/contexts/PreviewContext";
import { EmptyState } from "@/components/core/EmptyState";
import { Info } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export const PropertiesInspectorWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { session, artifacts } = usePreviewContext();
  const currentArtifact = artifacts.find(a => a.id === session.artifactId);
  const [activeTab, setActiveTab] = useState<'Properties' | 'Metadata' | 'Execution'>('Properties');

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  if (!currentArtifact) {
    return <Panel id="properties-inspector" header="Inspector"><EmptyState icon={Info} title="No Artifact" description="Select an artifact to inspect." /></Panel>;
  }

  return (
    <Panel id="properties-inspector" ref={panelRef} header="Inspector" className="h-full">
      <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex flex-col h-full">
        <div className="flex border-b border-glass-border mb-3">
          {['Properties', 'Metadata', 'Execution'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`flex-1 pb-2 text-xs font-medium border-b-2 transition-colors ${activeTab === tab ? 'border-accent-primary text-accent-primary' : 'border-transparent text-text-muted hover:text-text-primary'}`}
            >
              {tab}
            </button>
          ))}
        </div>
        
        {activeTab === 'Properties' && (
          <div className="flex flex-col space-y-3 text-sm">
            <div className="flex flex-col"><span className="text-xs text-text-muted">Name</span><span className="text-text-primary">{currentArtifact.name}</span></div>
            <div className="flex flex-col"><span className="text-xs text-text-muted">Type</span><span className="text-text-primary font-mono">{currentArtifact.mimeType}</span></div>
            <div className="flex flex-col"><span className="text-xs text-text-muted">Size</span><span className="text-text-primary">{(currentArtifact.sizeBytes / 1024).toFixed(2)} KB</span></div>
            <div className="flex flex-col"><span className="text-xs text-text-muted">Category</span><span className="text-text-primary capitalize">{currentArtifact.category}</span></div>
          </div>
        )}

        {activeTab === 'Metadata' && (
          <div className="flex flex-col space-y-3 text-sm">
            <div className="flex flex-col"><span className="text-xs text-text-muted">Author Agent</span><span className="text-text-primary">{currentArtifact.author}</span></div>
            <div className="flex flex-col"><span className="text-xs text-text-muted">Created</span><span className="text-text-primary font-mono">{currentArtifact.createdAt}</span></div>
            <div className="flex flex-col"><span className="text-xs text-text-muted">Tags</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {currentArtifact.tags.map(t => <span key={t} className="text-xs px-2 py-0.5 bg-surface-hover border border-glass-border rounded-full">{t}</span>)}
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </Panel>
  );
});
PropertiesInspectorWidget.displayName = "PropertiesInspectorWidget";
