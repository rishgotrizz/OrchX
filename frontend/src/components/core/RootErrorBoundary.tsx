"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { telemetry } from "@/lib/telemetry";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class RootErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    telemetry.trackError(error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen bg-void text-text-primary flex flex-col items-center justify-center p-8 space-y-4">
          <div className="bg-surface border border-glass-border p-6 rounded-lg max-w-2xl w-full shadow-glow">
            <h1 className="text-2xl font-semibold text-status-error mb-2">Fatal Error</h1>
            <p className="text-text-secondary mb-4">OrchX encountered a critical exception. The error has been logged to the telemetry engine.</p>
            <div className="bg-void p-4 rounded text-xs font-mono text-text-muted overflow-auto max-h-64 border border-glass-border">
              {this.state.error?.message}
            </div>
            <button 
              onClick={() => window.location.reload()}
              className="mt-6 px-4 py-2 bg-accent-primary text-void font-semibold rounded hover:bg-accent-secondary transition-colors"
            >
              Restart Runtime
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
