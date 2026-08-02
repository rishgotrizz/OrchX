"use client";

import React, { useState, useRef, useEffect } from "react";
import { MissionProvider } from "@/contexts/MissionContext";
import { Paperclip, Mic, ArrowUp, ChevronDown, FileText, Database, Box } from "lucide-react";
import Link from "next/link";

export default function MissionControlPage() {
  const [prompt, setPrompt] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!prompt.trim()) return;
    
    setIsChatting(true);
    const newMsg = { role: "user", content: prompt };
    setMessages(prev => [...prev, newMsg]);
    setPrompt("");

    // Mock AI response delay
    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: "I can help you build that. I've generated a Product Requirements Document (PRD) to define the scope.",
          artifacts: [
            { id: 1, type: "prd", title: "Ecommerce Platform MVP", status: "Generated Successfully", route: "/documents-studio" }
          ]
        }
      ]);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <MissionProvider>
      <div className="flex flex-col h-full bg-void">
        
        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto">
          {!isChatting ? (
            /* Empty State / Welcome Screen */
            <div className="h-full flex flex-col items-center justify-center max-w-3xl mx-auto px-4 pb-32">
              <div className="w-16 h-16 rounded-2xl bg-accent-primary flex items-center justify-center mb-8 shadow-glow">
                <span className="text-2xl text-white font-bold tracking-tighter">OX</span>
              </div>
              <h1 className="text-3xl font-medium text-text-primary mb-12">What would you like to build today?</h1>
              
              <div className="grid grid-cols-2 gap-4 w-full opacity-60">
                <button onClick={() => { setPrompt("Build me a CRM."); setIsChatting(true); handleSubmit(); }} className="text-left p-4 border border-glass-divider rounded-xl hover:bg-surface-hover transition-colors">
                  <h3 className="text-sm font-medium text-text-primary mb-1">Build CRM</h3>
                  <p className="text-xs text-text-muted">Start a new customer relationship management tool</p>
                </button>
                <button className="text-left p-4 border border-glass-divider rounded-xl hover:bg-surface-hover transition-colors">
                  <h3 className="text-sm font-medium text-text-primary mb-1">Create Ecommerce Store</h3>
                  <p className="text-xs text-text-muted">Generate a full-stack Next.js storefront</p>
                </button>
              </div>
            </div>
          ) : (
            /* Active Conversation Thread */
            <div className="max-w-3xl mx-auto px-4 py-12 flex flex-col space-y-8 pb-40">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="bg-surface-active px-5 py-3 rounded-2xl rounded-tr-sm max-w-[80%] text-text-primary text-[15px] leading-relaxed">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="flex flex-col space-y-4 max-w-[85%]">
                      <div className="text-text-primary text-[15px] leading-relaxed">
                        {msg.content}
                      </div>
                      
                      {/* Inline Artifact Cards */}
                      {msg.artifacts && msg.artifacts.map((artifact: any) => (
                        <div key={artifact.id} className="bg-surface border border-glass-border rounded-xl p-4 flex flex-col space-y-4 w-80 shadow-lg">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center space-x-2">
                              {artifact.type === 'prd' && <FileText className="w-4 h-4 text-accent-primary" />}
                              {artifact.type === 'database' && <Database className="w-4 h-4 text-status-success" />}
                              {artifact.type === 'architecture' && <Box className="w-4 h-4 text-status-warning" />}
                              <span className="font-medium text-text-primary text-sm">{artifact.title}</span>
                            </div>
                          </div>
                          <div className="text-xs text-status-success flex items-center space-x-1.5">
                            <div className="w-1.5 h-1.5 bg-status-success rounded-full" />
                            <span>{artifact.status}</span>
                          </div>
                          <div className="border-t border-glass-divider pt-3 flex items-center space-x-2">
                            <Link href={artifact.route} className="flex-1 text-center py-1.5 bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 rounded-lg text-xs font-medium transition-colors">
                              Open Project
                            </Link>
                            <button className="px-3 py-1.5 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded-lg text-xs transition-colors">
                              Regenerate
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Persistent Bottom Prompt */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-void via-void to-transparent pt-10 pb-8 px-4 flex justify-center">
          <div className="w-full max-w-3xl relative">
            <div className="bg-surface border border-glass-border rounded-2xl shadow-2xl flex flex-col">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask OrchX..."
                className="w-full bg-transparent resize-none p-4 pb-2 focus:outline-none text-text-primary placeholder:text-text-muted text-[15px] leading-relaxed max-h-48 overflow-y-auto"
                rows={1}
                style={{ minHeight: '60px' }}
              />
              <div className="flex items-center justify-between p-2 pt-0">
                <div className="flex items-center space-x-1">
                  <button className="p-2 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors">
                    <Paperclip className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors">
                    <Mic className="w-4 h-4" />
                  </button>
                  <div className="h-4 w-[1px] bg-glass-divider mx-1" />
                  <button className="flex items-center space-x-1 px-2 py-1.5 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors text-xs font-medium">
                    <span>OrchX-4</span>
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </div>
                <button 
                  onClick={handleSubmit}
                  disabled={!prompt.trim()}
                  className="p-2 bg-accent-primary text-white rounded-lg hover:bg-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowUp className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="text-center mt-3 text-[10px] text-text-muted/60">
              OrchX can make mistakes. Verify important information.
            </div>
          </div>
        </div>

      </div>
    </MissionProvider>
  );
}
