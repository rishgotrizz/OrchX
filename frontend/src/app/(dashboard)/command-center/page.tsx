"use client";
import { PageTransition } from "@/components/shared/PageTransition";
import { EmptyState } from "@/components/core/EmptyState";
import { Settings } from "lucide-react";

export default function CommandCenter() {
  return (
    <PageTransition>
      <div className="h-full flex flex-col p-6 space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Command Center</h1>
        <div className="flex-1 rounded-lg border border-glass-border bg-surface flex flex-col items-center justify-center">
          <EmptyState 
            icon={Settings} 
            title="Configuration" 
            description="Configure OrchX to match your workflow." 
          />
        </div>
      </div>
    </PageTransition>
  )
}
