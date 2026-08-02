"use client";

import React from "react";
import { Group as PanelGroup, Panel as ResizablePanel, Separator as PanelResizeHandle } from "react-resizable-panels";
import { cn } from "@/lib/utils";
import { eventBus } from "@/lib/event-bus";

interface ResizableSplitPaneProps {
  id: string;
  direction: "horizontal" | "vertical";
  panels: {
    id: string;
    content: React.ReactNode;
    defaultSize?: number;
    minSize?: number;
    maxSize?: number;
    collapsible?: boolean;
  }[];
  className?: string;
}

export function ResizableSplitPane({ id, direction, panels, className }: ResizableSplitPaneProps) {
  const handleLayout = (newSizes: any) => {
    if (Array.isArray(newSizes)) {
      panels.forEach((p, idx) => {
        eventBus.emit('ui.panel.resized', { panelId: p.id, size: newSizes[idx] });
      });
    } else {
      Object.entries(newSizes).forEach(([panelId, size]) => {
        eventBus.emit('ui.panel.resized', { panelId, size: size as number });
      });
    }
  };

  return (
    <PanelGroup 
      id={`split-pane-${id}`}
      orientation={direction} 
      onLayoutChange={handleLayout}
      className={cn("w-full h-full", className)}
    >
      {panels.map((panel, idx) => (
        <React.Fragment key={panel.id}>
          <ResizablePanel
            id={panel.id}
            defaultSize={panel.defaultSize || (100 / panels.length)}
            minSize={panel.minSize || 10}
            maxSize={panel.maxSize || 100}
            collapsible={panel.collapsible}
            className="flex flex-col relative"
          >
            {panel.content}
          </ResizablePanel>
          
          {idx < panels.length - 1 && (
            <PanelResizeHandle 
              className={cn(
                "relative flex items-center justify-center bg-transparent transition-colors group",
                direction === "horizontal" ? "w-1 cursor-col-resize" : "h-1 cursor-row-resize"
              )}
            >
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity delay-100">
                <div className="w-full h-full bg-accent-primary/30" />
              </div>
            </PanelResizeHandle>
          )}
        </React.Fragment>
      ))}
    </PanelGroup>
  );
}
