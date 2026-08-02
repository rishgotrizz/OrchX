"use client";

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { WORKSPACE_REGISTRY } from "@/lib/workspace-registry"
import { Plus, Search, MessageSquare, Box, Settings, Activity, MonitorPlay } from "lucide-react"

const MOCK_HISTORY = [
  { id: 1, title: "Build CRM", group: "Today" },
  { id: 2, title: "Create Ecommerce Store", group: "Today" },
  { id: 3, title: "Build Portfolio", group: "Yesterday" },
  { id: 4, title: "Research AI Agents", group: "Older" },
];

export function Dock() {
  const pathname = usePathname()

  const getFriendlyName = (id: string) => {
    if (id === 'mission-control') return { title: 'Home', icon: MessageSquare };
    if (id === 'documents-studio') return { title: 'Projects', icon: Box };
    if (id === 'runtime-observatory') return { title: 'Runtime', icon: Activity };
    if (id === 'preview-studio') return { title: 'Preview', icon: MonitorPlay };
    if (id === 'command-center') return { title: 'Settings', icon: Settings };
    return null;
  }

  const primaryWorkspaces = WORKSPACE_REGISTRY.map(w => ({ ...w, friendly: getFriendlyName(w.id) })).filter(w => w.friendly !== null);

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-surface flex flex-col border-r border-glass-divider z-30" aria-label="Main Navigation">
      
      {/* Header */}
      <div className="p-4 flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center shadow-glow">
          <span className="text-sm text-white font-bold tracking-tighter">OX</span>
        </div>
        <span className="text-lg font-medium text-text-primary tracking-tight">OrchX</span>
      </div>

      {/* Top Actions */}
      <div className="px-3 pb-3 space-y-2">
        <Link href="/mission-control" className="flex items-center justify-between px-3 py-2 bg-void border border-glass-border rounded-md text-sm text-text-primary hover:bg-surface-hover transition-colors group">
          <span className="font-medium flex items-center gap-2">
            New Chat
          </span>
          <Plus className="w-4 h-4 text-text-muted group-hover:text-text-primary transition-colors" />
        </Link>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input type="text" placeholder="Search..." className="w-full bg-void border border-glass-border rounded-md pl-9 pr-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-primary" />
        </div>
      </div>

      {/* History */}
      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        {['Today', 'Yesterday', 'Older'].map(group => {
          const items = MOCK_HISTORY.filter(h => h.group === group);
          if (items.length === 0) return null;
          return (
            <div key={group} className="space-y-1">
              <h4 className="text-xs font-semibold text-text-muted px-2">{group}</h4>
              <div className="flex flex-col">
                {items.map(item => (
                  <button key={item.id} className="text-left px-2 py-1.5 text-sm text-text-secondary hover:bg-surface-hover hover:text-text-primary rounded-md truncate transition-colors">
                    {item.title}
                  </button>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Primary Workspaces */}
      <div className="p-3 border-t border-glass-divider space-y-0.5">
        {primaryWorkspaces.map((workspace) => {
          const isActive = pathname?.startsWith(workspace.route)
          const Icon = workspace.friendly!.icon;
          
          return (
            <Link 
              key={workspace.id}
              href={workspace.route}
              className={`relative flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-surface-active text-text-primary font-medium' : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="text-sm">{workspace.friendly!.title}</span>
            </Link>
          )
        })}
      </div>
    </aside>
  )
}
