import * as React from "react"
import { Search, Bell, User } from "lucide-react"

export function KernelBar() {
  return (
    <header className="h-12 w-full flex items-center justify-between px-4 bg-void/80 backdrop-blur-md fixed top-0 left-0 z-50">
      <div className="flex items-center space-x-6">
        <div className="text-lg font-bold tracking-tight text-text-primary">OrchX</div>
        <div className="flex items-center space-x-2 text-sm text-text-muted cursor-pointer hover:text-text-primary transition-colors">
          <span>Project: Alpha</span>
          <span className="text-[10px] opacity-50">▼</span>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 px-2 py-1 rounded bg-surface hover:bg-surface-hover text-sm text-text-muted cursor-text transition-colors">
          <Search className="w-3.5 h-3.5" />
          <span>⌘K Search</span>
        </div>
        
        <div className="flex items-center space-x-4 text-text-muted">
          <button className="hover:text-text-primary transition-colors"><Bell className="w-4 h-4" /></button>
          <div className="font-mono text-sm">₡ 847</div>
          <button className="w-6 h-6 rounded-full bg-surface-active flex items-center justify-center hover:bg-surface-hover transition-colors text-text-primary">
            <User className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  )
}
