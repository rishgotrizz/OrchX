"use client";

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { WORKSPACE_REGISTRY } from "@/lib/workspace-registry"
import { Plus, Search, MessageSquare, Box, Settings, Activity, MonitorPlay, Info, X } from "lucide-react"

export interface ChatHistoryItem {
  id: string;
  title: string;
  createdAt: string;
}

export function Dock() {
  const pathname = usePathname()
  const [chatHistory, setChatHistory] = React.useState<ChatHistoryItem[]>([])
  const [searchQuery, setSearchQuery] = React.useState("")

  const loadChatHistory = React.useCallback(() => {
    if (typeof window !== 'undefined') {
      try {
        const items = JSON.parse(localStorage.getItem('orchx_chat_history') || '[]')
        setChatHistory(items)
      } catch (e) {
        setChatHistory([])
      }
    }
  }, [])

  React.useEffect(() => {
    loadChatHistory()
    if (typeof window !== 'undefined') {
      window.addEventListener('orchx_chat_updated', loadChatHistory)
      return () => window.removeEventListener('orchx_chat_updated', loadChatHistory)
    }
  }, [loadChatHistory])

  const handleDeleteChat = (id: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const updated = chatHistory.filter(c => c.id !== id)
    setChatHistory(updated)
    if (typeof window !== 'undefined') {
      localStorage.setItem('orchx_chat_history', JSON.stringify(updated))
      window.dispatchEvent(new Event('orchx_chat_updated'))
    }
  }

  const filteredChats = searchQuery.trim() 
    ? chatHistory.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : chatHistory

  const getFriendlyName = (id: string) => {
    if (id === 'mission-control') return { title: 'Home', icon: MessageSquare, desc: 'Side-by-side autonomous agent execution and live project sandbox preview' };
    if (id === 'documents-studio') return { title: 'Projects', icon: Box, desc: 'Knowledge vault, specifications, architecture blueprints, and document editor' };
    if (id === 'runtime-observatory') return { title: 'Runtime', icon: Activity, desc: 'Live kernel telemetry, active worker pool, and circuit-breaker provider routing' };
    if (id === 'command-center') return { title: 'Settings', icon: Settings, desc: 'Provider key management, SecretVault policies, and system configuration', route: '/settings-studio' };
    return null;
  }

  const primaryWorkspaces = WORKSPACE_REGISTRY.map(w => ({ ...w, friendly: getFriendlyName(w.id) })).filter(w => w.friendly !== null);

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-surface flex flex-col border-r border-glass-divider z-30" aria-label="Main Navigation">
      
      {/* Header */}
      <div className="p-4 flex items-center justify-between">
        <span className="text-xl font-bold text-text-primary tracking-tight">OrchX</span>
        <div className="relative group/headinfo">
          <button 
            type="button"
            className="p-1 text-text-muted hover:text-accent-primary transition-colors"
          >
            <Info className="w-4 h-4" />
          </button>
          <div className="absolute left-full top-0 ml-2 w-60 p-2.5 bg-surface border border-glass-border rounded-xl shadow-2xl text-xs text-text-secondary opacity-0 pointer-events-none group-hover/headinfo:opacity-100 group-hover/headinfo:pointer-events-auto transition-opacity z-50">
            <span className="font-semibold text-text-primary block mb-1">OrchX Enterprise</span>
            Universal multi-agent orchestration engine with zero-trust SecretVault and circuit-breaker provider routing.
          </div>
        </div>
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
          <input 
            type="text" 
            placeholder="Search chats..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-void border border-glass-border rounded-md pl-9 pr-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-primary" 
          />
        </div>
      </div>

      {/* Navigation Space / Recent Chat History */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-3">
        {filteredChats.length > 0 && (
          <div className="space-y-1">
            <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider px-2 block mb-1">
              Recent Chats
            </span>
            {filteredChats.map((chat) => (
              <div
                key={chat.id}
                className="group flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-surface-hover text-xs text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
              >
                <Link
                  href={`/mission-control?chat=${chat.id}&mission=${encodeURIComponent(chat.title)}`}
                  className="flex items-center space-x-2 overflow-hidden flex-1 min-w-0"
                >
                  <MessageSquare className="w-3.5 h-3.5 opacity-60 shrink-0 text-accent-primary" />
                  <span className="truncate">{chat.title}</span>
                </Link>
                
                <button
                  type="button"
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  className="p-1 text-text-muted hover:text-status-error opacity-0 group-hover:opacity-100 transition-opacity rounded"
                  title="Delete Chat"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Primary Workspaces */}
      <div className="p-3 border-t border-glass-divider space-y-0.5">
        {primaryWorkspaces.map((workspace) => {
          const isActive = pathname?.startsWith(workspace.route)
          const Icon = workspace.friendly!.icon;
          const desc = workspace.friendly!.desc;
          
          return (
            <div key={workspace.id} className="relative group/navitem flex items-center">
              <Link 
                href={workspace.friendly?.route || workspace.route}
                className={`flex-1 flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-surface-active text-text-primary font-medium' : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="text-sm">{workspace.friendly!.title}</span>
              </Link>
              <div className="relative group/info pr-2">
                <button 
                  type="button"
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}
                  className="p-1 text-text-muted hover:text-accent-primary transition-colors rounded"
                >
                  <Info className="w-3.5 h-3.5" />
                </button>
                <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 w-56 p-2.5 bg-surface border border-glass-border rounded-xl shadow-2xl text-xs text-text-secondary opacity-0 pointer-events-none group-hover/info:opacity-100 group-hover/info:pointer-events-auto transition-opacity z-50">
                  <span className="font-semibold text-text-primary block mb-0.5">{workspace.friendly!.title}</span>
                  {desc}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </aside>
  )
}
