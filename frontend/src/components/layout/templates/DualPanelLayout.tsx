import React from "react";
import { ResizableSplitPane } from "@/components/layout/ResizableSplitPane";

export function DualPanelLayout({
  id,
  leftPanel,
  rightPanel,
  leftSize = 25,
  rightSize = 75,
  title
}: {
  id: string;
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  leftSize?: number;
  rightSize?: number;
  title?: string;
}) {
  return (
    <div className="flex flex-col h-full w-full">
      {title && (
        <div className="px-8 py-6 shrink-0 bg-void">
          <h1 className="text-2xl font-light text-text-primary tracking-tight">{title}</h1>
        </div>
      )}
      <div className="flex-1 relative bg-void">
        <ResizableSplitPane
          id={id}
          direction="horizontal"
          panels={[
            { id: `${id}-left`, content: leftPanel, defaultSize: leftSize },
            { id: `${id}-right`, content: rightPanel, defaultSize: rightSize },
          ]}
        />
      </div>
    </div>
  );
}
