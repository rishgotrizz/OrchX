"use client";

import React, { forwardRef, useImperativeHandle, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { eventBus } from "@/lib/event-bus";
import { cn } from "@/lib/utils";

export interface PanelRef {
  open: () => void;
  close: () => void;
  collapse: () => void;
  expand: () => void;
  fullscreen: () => void;
  restore: () => void;
  focus: () => void;
}

export interface PanelProps {
  id: string;
  className?: string;
  header?: React.ReactNode;
  subHeader?: React.ReactNode;
  toolbar?: React.ReactNode;
  actions?: React.ReactNode;
  statusIndicator?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  defaultCollapsed?: boolean;
}

export const Panel = forwardRef<PanelRef, PanelProps>(({
  id,
  className,
  header,
  subHeader,
  toolbar,
  actions,
  statusIndicator,
  footer,
  children,
  defaultCollapsed = false,
}, ref) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isOpen, setIsOpen] = useState(true);

  useImperativeHandle(ref, () => ({
    open: () => { setIsOpen(true); eventBus.emit('ui.panel.opened', { panelId: id }); },
    close: () => { setIsOpen(false); eventBus.emit('ui.panel.closed', { panelId: id }); },
    collapse: () => { setIsCollapsed(true); eventBus.emit('ui.panel.collapsed', { panelId: id }); },
    expand: () => { setIsCollapsed(false); eventBus.emit('ui.panel.expanded', { panelId: id }); },
    fullscreen: () => { setIsFullscreen(true); eventBus.emit('ui.panel.fullscreen', { panelId: id }); },
    restore: () => { setIsFullscreen(false); eventBus.emit('ui.panel.restored', { panelId: id }); },
    focus: () => {
      eventBus.emit('ui.panel.focused', { panelId: id });
    }
  }));

  if (!isOpen) return null;

  return (
    <motion.div
      layout
      className={cn(
        "flex flex-col bg-transparent overflow-hidden transition-shadow focus-within:ring-1 focus-within:ring-accent-primary/20",
        isFullscreen ? "fixed inset-0 z-50 bg-void" : "w-full h-full relative",
        className
      )}
      onFocus={() => eventBus.emit('ui.panel.focused', { panelId: id })}
      onBlur={() => eventBus.emit('ui.panel.blurred', { panelId: id })}
      tabIndex={-1}
    >
      {/* Panel Headers have been globally removed to eliminate dashboard styling */}
      
      {subHeader && (
        <div className="px-4 py-2 shrink-0 bg-transparent">
          {subHeader}
        </div>
      )}

      {/* Toolbars have been globally removed to eliminate dashboard styling */}

      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.div
            initial="collapsed"
            animate="expanded"
            exit="collapsed"
            variants={{
              expanded: { opacity: 1, height: "auto" },
              collapsed: { opacity: 0, height: 0 }
            }}
            transition={{ type: "spring", stiffness: 400, damping: 40 }}
            className="flex-1 overflow-auto p-4"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>

      {footer && !isCollapsed && (
        <footer className="px-4 py-2 shrink-0 bg-transparent text-xs text-text-muted">
          {footer}
        </footer>
      )}
    </motion.div>
  );
});

Panel.displayName = "Panel";
