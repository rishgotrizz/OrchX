import * as React from "react"
import { ListTodo, Cpu, Zap, Link as LinkIcon } from "lucide-react"

export function StatusRail() {
  return (
    <footer className="h-7 w-full flex items-center justify-between px-4 bg-void/80 backdrop-blur-md fixed bottom-0 left-0 z-40 text-[11px] font-mono text-text-muted">
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-status-healthy">
          <div className="w-2 h-2 rounded-full bg-status-healthy shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-[pulse_4s_ease-in-out_infinite]" />
          <span>Healthy</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <ListTodo className="w-3.5 h-3.5" />
          <span>0 Tasks</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Cpu className="w-3.5 h-3.5" />
          <span>0 Workers</span>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 text-text-secondary">
          <Zap className="w-3.5 h-3.5" />
          <span>0ms</span>
        </div>
        <div className="flex items-center space-x-1.5 text-text-disabled">
          <LinkIcon className="w-3.5 h-3.5" />
          <span>Disconnected</span>
        </div>
      </div>
    </footer>
  )
}
