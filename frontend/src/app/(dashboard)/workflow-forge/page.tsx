"use client";
import { PageTransition } from "@/components/shared/PageTransition";
import { EmptyState } from "@/components/core/EmptyState";
import { Workflow } from "lucide-react";

export default function WorkflowForge() {
  return (
    <PageTransition>
      <div className="h-full flex flex-col p-6 space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Workflow Forge</h1>
        <div className="flex-1 rounded-lg border border-glass-border bg-surface flex flex-col items-center justify-center relative bg-[url('/dots.svg')] bg-repeat">
          <EmptyState 
            icon={Workflow} 
            title="Canvas is empty" 
            description="Create or import a workflow to begin orchestration." 
          />
        </div>
      </div>
    </PageTransition>
  )
}
