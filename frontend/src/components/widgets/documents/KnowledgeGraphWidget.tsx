"use client";

import React, { useRef, useImperativeHandle, forwardRef } from "react";
import { Panel, PanelRef } from "@/components/layout/Panel";
import { ReactFlow, Background, Controls } from "@xyflow/react";
import '@xyflow/react/dist/style.css';
import { useDocumentsContext } from "@/contexts/DocumentsContext";

export const KnowledgeGraphWidget = forwardRef((props, ref) => {
  const panelRef = useRef<PanelRef>(null);
  const { documents } = useDocumentsContext();

  useImperativeHandle(ref, () => ({
    initialize: () => {}, mount: () => {}, refresh: () => {}, sleep: () => {}, resume: () => {}, destroy: () => {}, onVisibilityChange: () => {}, onPermissionChange: () => {},
  }));

  const nodes = documents.map((doc, i) => ({
    id: doc.id,
    position: { x: (i % 2) * 150 + 50, y: Math.floor(i / 2) * 100 + 50 },
    data: { label: doc.title },
    style: { background: 'var(--color-surface)', color: 'var(--color-text-primary)', border: '1px solid var(--color-glass-border)', borderRadius: '8px', padding: '10px', fontSize: '12px' }
  }));

  const edges = documents.length > 1 ? [
    { id: 'e1-2', source: documents[0]?.id, target: documents[1]?.id, animated: true, style: { stroke: 'var(--color-accent-primary)' } }
  ] : [];

  return (
    <Panel id="knowledge-graph" ref={panelRef} header="Knowledge Graph" className="h-full">
      <div className="h-full w-full bg-void rounded border border-glass-border overflow-hidden">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="var(--color-glass-border)" gap={20} />
          <Controls showInteractive={false} className="!bg-surface !border-glass-border !fill-text-primary" />
        </ReactFlow>
      </div>
    </Panel>
  );
});
KnowledgeGraphWidget.displayName = "KnowledgeGraphWidget";
