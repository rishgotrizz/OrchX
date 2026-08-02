"use client";

import { useEffect } from "react";
import { PageTransition } from "@/components/shared/PageTransition";
import { AlertOctagon, RefreshCw, Copy, Home } from "lucide-react";
import { Button } from "@/components/core/Button";
import { useRouter } from "next/navigation";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Kernel Exception:", error);
  }, [error]);

  return (
    <PageTransition>
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-status-error/10 border border-status-error/20 p-8 rounded-xl max-w-lg w-full shadow-[0_0_40px_rgba(239,68,68,0.1)]">
          <AlertOctagon className="w-12 h-12 text-status-error mx-auto mb-4" />
          <h2 className="text-xl font-bold text-text-primary mb-2 tracking-tight">Kernel Exception</h2>
          <p className="text-sm text-text-secondary mb-6">{error.message || "An unexpected orchestration error occurred."}</p>
          
          <div className="bg-void-elevated rounded-md p-3 text-xs font-mono text-text-muted text-left mb-6 overflow-x-auto border border-glass-border">
            <div className="flex justify-between items-center mb-1">
              <span>DIAGNOSTIC_ID:</span>
              <span>{error.digest || Math.random().toString(36).substring(7).toUpperCase()}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>TIMESTAMP:</span>
              <span>{new Date().toISOString()}</span>
            </div>
          </div>

          <div className="flex items-center justify-center space-x-3">
            <Button variant="ghost" size="sm" onClick={() => router.push("/mission-control")}>
              <Home className="w-4 h-4 mr-2" />
              Mission Control
            </Button>
            <Button variant="default" size="sm" onClick={() => navigator.clipboard.writeText(`${error.message}\nDigest: ${error.digest}`)}>
              <Copy className="w-4 h-4 mr-2" />
              Copy Report
            </Button>
            <Button variant="primary" size="sm" onClick={() => reset()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
