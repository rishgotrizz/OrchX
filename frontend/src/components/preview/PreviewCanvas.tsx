"use client";

import React from "react";
import { usePreviewContext } from "@/contexts/PreviewContext";
import { getRendererForMimeType } from "@/lib/renderer-registry";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import { EmptyState } from "@/components/core/EmptyState";
import { FileQuestion, Maximize, ZoomIn, ZoomOut } from "lucide-react";
import { motion } from "framer-motion";
import { fadeIn } from "@/lib/motion";

export function PreviewCanvas() {
  const { session, artifacts } = usePreviewContext();
  const currentArtifact = artifacts.find(a => a.id === session.artifactId);
  
  if (!currentArtifact) {
    return (
      <div className="flex-1 flex items-center justify-center bg-void rounded-lg border border-glass-border">
        <EmptyState icon={FileQuestion} title="No Artifact Selected" description="Select an artifact from the explorer." />
      </div>
    );
  }

  const RendererDef = getRendererForMimeType(currentArtifact.mimeType);
  
  if (!RendererDef) {
    return (
      <div className="flex-1 flex items-center justify-center bg-void rounded-lg border border-glass-border">
        <EmptyState icon={FileQuestion} title="No Renderer Found" description={`No preview driver installed for ${currentArtifact.mimeType}.`} />
      </div>
    );
  }

  const Renderer = RendererDef.component;

  const frameSizes = {
    desktop: { width: '100%', height: '100%', border: 'none', borderRadius: '0' },
    laptop: { width: '1280px', height: '800px', border: '1px solid var(--color-glass-border)', borderRadius: '8px' },
    tablet: { width: '768px', height: '1024px', border: '1px solid var(--color-glass-border)', borderRadius: '12px' },
    mobile: { width: '375px', height: '812px', border: '1px solid var(--color-glass-border)', borderRadius: '24px' },
    responsive: { width: '100%', height: '100%', border: 'none', borderRadius: '0' }
  };
  const frameStyle = frameSizes[session.deviceProfile] || frameSizes.responsive;

  const enableTransforms = session.deviceProfile !== 'responsive' && session.deviceProfile !== 'desktop';

  return (
    <motion.div variants={fadeIn} initial="initial" animate="animate" exit="exit" className="flex-1 flex flex-col h-full w-full bg-void rounded-lg border border-glass-border overflow-hidden relative">
      <TransformWrapper 
        initialScale={1} 
        minScale={0.1} 
        maxScale={4}
        centerOnInit
        disabled={!enableTransforms}
      >
        {({ zoomIn, zoomOut, resetTransform }) => (
          <>
            {enableTransforms && (
              <div className="absolute bottom-4 right-4 z-10 flex space-x-2 bg-surface p-1 rounded border border-glass-border shadow-glow">
                <button onClick={() => zoomIn()} className="p-1.5 hover:bg-surface-hover rounded text-text-secondary hover:text-text-primary"><ZoomIn className="w-4 h-4" /></button>
                <button onClick={() => zoomOut()} className="p-1.5 hover:bg-surface-hover rounded text-text-secondary hover:text-text-primary"><ZoomOut className="w-4 h-4" /></button>
                <button onClick={() => resetTransform()} className="p-1.5 hover:bg-surface-hover rounded text-text-secondary hover:text-text-primary"><Maximize className="w-4 h-4" /></button>
              </div>
            )}
            <TransformComponent wrapperClass="!w-full !h-full" contentClass="!w-full !h-full flex items-center justify-center p-4">
               <div style={{ ...frameStyle, transition: 'all 0.3s ease' }} className="bg-surface overflow-auto shadow-glow flex flex-col">
                 <Renderer artifact={currentArtifact} session={session} />
               </div>
            </TransformComponent>
          </>
        )}
      </TransformWrapper>
    </motion.div>
  );
}
