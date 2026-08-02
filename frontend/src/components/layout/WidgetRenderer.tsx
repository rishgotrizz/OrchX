"use client";

import React, { Suspense, useEffect, useRef } from "react";
import { getWidget } from "@/lib/widget-registry";
import { PanelSkeleton } from "@/components/core/Skeleton";
import { EmptyState } from "@/components/core/EmptyState";
import { AlertTriangle } from "lucide-react";
import { Panel } from "@/components/layout/Panel";
import { ErrorBoundary } from "react-error-boundary";

export function WidgetRenderer({ widgetId }: { widgetId: string }) {
  const widget = getWidget(widgetId);
  const widgetRef = useRef<any>(null);

  useEffect(() => {
    if (widgetRef.current) {
      widgetRef.current.initialize?.();
      widgetRef.current.mount?.();
      widgetRef.current.resume?.();
    }
    return () => {
      if (widgetRef.current) {
        widgetRef.current.sleep?.();
        widgetRef.current.destroy?.();
      }
    };
  }, []);

  if (!widget) {
    return (
      <Panel id={`missing-${widgetId}`} header="Widget Missing">
        <EmptyState 
          icon={AlertTriangle} 
          title="Widget Not Found" 
          description={`The widget ${widgetId} is not registered in the Widget Registry.`} 
        />
      </Panel>
    );
  }

  const WidgetComponent = widget.component;

  return (
    <ErrorBoundary fallback={
      <Panel id={`error-${widgetId}`} header={widget.title}>
        <EmptyState 
          icon={AlertTriangle} 
          title="Widget Error" 
          description={`The widget ${widget.title} encountered an execution fault.`} 
        />
      </Panel>
    }>
      <Suspense fallback={<PanelSkeleton />}>
        <WidgetComponent ref={widgetRef} />
      </Suspense>
    </ErrorBoundary>
  );
}
