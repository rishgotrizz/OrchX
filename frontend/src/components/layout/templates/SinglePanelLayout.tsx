import React from "react";
import { Breadcrumbs, BreadcrumbSegment } from "@/components/layout/Breadcrumbs";

export function SinglePanelLayout({
  children,
  breadcrumbs
}: {
  children: React.ReactNode;
  breadcrumbs?: BreadcrumbSegment[];
}) {
  return (
    <div className="flex flex-col h-full w-full">
      {breadcrumbs && (
        <div className="px-4 py-2 border-b border-glass-border shrink-0 bg-void/50 backdrop-blur-sm z-10">
          <Breadcrumbs segments={breadcrumbs} />
        </div>
      )}
      <div className="flex-1 relative bg-surface p-4 overflow-hidden">
        {children}
      </div>
    </div>
  );
}
