"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useUiStore } from "@/stores/uiStore";
import { useLocalStorage } from "usehooks-ts";

export function Inspector() {
  const isInspectorOpen = useUiStore((state) => state.isInspectorOpen);
  const toggleInspector = useUiStore((state) => state.toggleInspector);
  const [width, setWidth] = useLocalStorage("inspector-width", 320);
  const isDragging = React.useRef(false);

  const handleMouseDown = React.useCallback(() => {
    isDragging.current = true;
    document.body.style.cursor = 'ew-resize';
    document.body.style.userSelect = 'none';
  }, []);

  const handleMouseUp = React.useCallback(() => {
    isDragging.current = false;
    document.body.style.cursor = 'default';
    document.body.style.userSelect = 'auto';
  }, []);

  const handleMouseMove = React.useCallback((e: MouseEvent) => {
    if (!isDragging.current) return;
    const newWidth = window.innerWidth - e.clientX;
    // Constrain width between 200px and 600px
    if (newWidth > 200 && newWidth < 600) {
      setWidth(newWidth);
    }
  }, [setWidth]);

  React.useEffect(() => {
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  return (
    <AnimatePresence initial={false}>
      {isInspectorOpen && (
        <motion.aside
          initial={{ width: 0, opacity: 0 }}
          animate={{ width, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="h-full bg-void-elevated border-l border-glass-border flex-shrink-0 relative flex flex-col"
        >
          {/* Resize Handle */}
          <div 
            className="absolute left-0 top-0 bottom-0 w-1.5 -ml-[1px] cursor-ew-resize hover:bg-accent-primary/50 transition-colors z-10"
            onMouseDown={handleMouseDown}
          />
          
          <div className="flex items-center justify-between px-4 h-12 border-b border-glass-border flex-shrink-0">
            <h2 className="text-sm font-semibold tracking-wide uppercase text-text-secondary">Inspector</h2>
            <button 
              onClick={toggleInspector}
              className="text-text-muted hover:text-text-primary px-1.5 py-0.5 rounded text-xs font-mono border border-glass-border hover:bg-surface-hover"
              aria-label="Close Inspector"
            >
              ⌘\
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-lg bg-surface-active border border-glass-border flex items-center justify-center mb-4">
              <span className="text-text-muted">⌘I</span>
            </div>
            <h3 className="text-sm font-medium text-text-primary mb-1">No Item Selected</h3>
            <p className="text-xs text-text-muted px-4">
              Select an element in the workspace to view its properties.
            </p>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
