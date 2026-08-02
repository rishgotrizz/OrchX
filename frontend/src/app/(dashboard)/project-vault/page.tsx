"use client";
import { PageTransition } from "@/components/shared/PageTransition";
import { EmptyState } from "@/components/core/EmptyState";
import { FolderGit2 } from "lucide-react";
import { Button } from "@/components/core/Button";

export default function ProjectVault() {
  return (
    <PageTransition>
      <div className="h-full flex flex-col p-6 space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Project Vault</h1>
        <div className="flex-1 rounded-lg border border-glass-border bg-surface flex flex-col items-center justify-center">
          <EmptyState 
            icon={FolderGit2} 
            title="No projects available." 
            description="Create your first workspace." 
            action={<Button variant="primary">Create Project</Button>}
          />
        </div>
      </div>
    </PageTransition>
  )
}
