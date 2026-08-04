"use client";

import React, { useState, useRef, useEffect } from "react";
import { MissionProvider } from "@/contexts/MissionContext";
import { Paperclip, Mic, ArrowUp, ChevronDown, FileText, Database, Box, Info } from "lucide-react";
import Link from "next/link";

export default function MissionControlPage() {
  const [prompt, setPrompt] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e?: React.FormEvent, customPrompt?: string) => {
    e?.preventDefault();
    const textToSubmit = customPrompt || prompt;
    if (!textToSubmit.trim()) return;
    
    setIsChatting(true);
    const newMsg = { role: "user", content: textToSubmit };
    setMessages(prev => [...prev, newMsg]);
    setPrompt("");

    // Helper to generate dynamic title from user input
    const cleanText = textToSubmit
      .replace(/^i (wanna|want to|would like to) (build|create|make)/i, '')
      .replace(/^(build|create|make)/i, '')
      .trim();

    const titleSubject = cleanText 
      ? cleanText.charAt(0).toUpperCase() + cleanText.slice(1) 
      : textToSubmit.trim();

    const cardTitle = titleSubject.toLowerCase().includes('prd') || titleSubject.toLowerCase().includes('mvp')
      ? titleSubject
      : `${titleSubject} PRD`;

    // Dynamic task & decision generation based on user goal
    setTimeout(() => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('orchx_active_mission', titleSubject);

        const existingHistory = JSON.parse(localStorage.getItem('orchx_chat_history') || '[]');
        const newHistoryItem = { id: `chat-${Date.now()}`, title: titleSubject, createdAt: new Date().toISOString() };
        const updatedHistory = [newHistoryItem, ...existingHistory.filter((item: any) => item.title !== titleSubject)];
        localStorage.setItem('orchx_chat_history', JSON.stringify(updatedHistory));
        window.dispatchEvent(new Event('orchx_chat_updated'));
      }

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: `I've analyzed your goal and initialized an autonomous mission execution plan for ${titleSubject}.`,
          missionName: titleSubject,
          tasks: [
            { id: 't-1', name: `Define ${titleSubject} Architecture & Scope`, status: 'Completed', detail: 'Analyzed domain model, core schemas, and interfaces.' },
            { id: 't-2', name: 'Construct Interactive UI Components', status: 'In Progress', detail: 'Building responsive layouts and state handlers.' },
            { id: 't-3', name: 'Wire State Engine & Data Persistence', status: 'Queued', detail: 'Setting up SQLite stores and event bus contracts.' },
            { id: 't-4', name: 'Autonomous Testing & Vercel Deployment', status: 'Queued', detail: 'Running smoke tests and verifying production routes.' }
          ],
          decisions: [
            { id: 'd-1', title: 'Tech Stack', choice: 'Next.js 16 (Turbopack) + Tailwind CSS', reason: 'Ensures sub-second static page compilation and responsive UI rendering.' },
            { id: 'd-2', title: 'Security Policy', choice: 'SecretVault AES-256-GCM + RBAC', reason: 'Zero-trust credential isolation protecting runtime secrets.' },
            { id: 'd-3', title: 'Resilience Strategy', choice: 'Circuit Breaker Failover Routing', reason: 'Sub-millisecond failover protection against upstream rate limits.' }
          ]
        }
      ]);
    }, 1200);
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
              <h1 className="text-3xl font-medium text-text-primary mb-12">What would you like to build today?</h1>
              
              <div className="grid grid-cols-2 gap-4 w-full opacity-60">
                <button onClick={() => handleSubmit(undefined, "Build a CRM Platform")} className="text-left p-4 border border-glass-divider rounded-xl hover:bg-surface-hover transition-colors">
                  <h3 className="text-sm font-medium text-text-primary mb-1">Build CRM</h3>
                  <p className="text-xs text-text-muted">Start a new customer relationship management tool</p>
                </button>
                <button onClick={() => handleSubmit(undefined, "Create Ecommerce Store")} className="text-left p-4 border border-glass-divider rounded-xl hover:bg-surface-hover transition-colors">
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
                    <div className="flex flex-col space-y-4 max-w-[90%] w-full">
                      <div className="text-text-primary text-[15px] leading-relaxed">
                        {msg.content}
                      </div>
                      
                      {/* Autonomous Task Plan Card */}
                      {msg.tasks && (
                        <div className="bg-surface border border-glass-border rounded-xl p-5 flex flex-col space-y-4 shadow-lg w-full">
                          <div className="flex items-center justify-between border-b border-glass-divider pb-3">
                            <span className="font-medium text-text-primary text-sm flex items-center gap-2">
                              <Box className="w-4 h-4 text-accent-primary" /> Autonomous Action Plan
                              <div className="relative group/info inline-block">
                                <button type="button" className="p-0.5 text-text-muted hover:text-accent-primary transition-colors">
                                  <Info className="w-3.5 h-3.5" />
                                </button>
                                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-2.5 bg-void border border-glass-border rounded-xl shadow-2xl text-[11px] text-text-secondary opacity-0 pointer-events-none group-hover/info:opacity-100 transition-opacity z-50">
                                  Sequenced execution steps generated by OrchX planner to fulfill your goal.
                                </div>
                              </div>
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-accent-primary/10 text-accent-primary font-mono uppercase">
                              Active Mission
                            </span>
                          </div>

                          <div className="flex flex-col space-y-2.5">
                            {msg.tasks.map((task: any) => (
                              <div key={task.id} className="flex items-start justify-between p-2.5 bg-void/50 border border-glass-divider rounded-lg">
                                <div className="flex flex-col space-y-0.5">
                                  <span className="text-xs font-medium text-text-primary">{task.name}</span>
                                  <span className="text-[11px] text-text-muted">{task.detail}</span>
                                </div>
                                <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded shrink-0 ml-3 ${
                                  task.status === 'Completed' ? 'bg-status-success/10 text-status-success' :
                                  task.status === 'In Progress' ? 'bg-status-warning/10 text-status-warning animate-pulse' :
                                  'bg-surface-hover text-text-muted'
                                }`}>
                                  {task.status}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Autonomous Decision Ledger Card */}
                      {msg.decisions && (
                        <div className="bg-surface border border-glass-border rounded-xl p-5 flex flex-col space-y-4 shadow-lg w-full">
                          <div className="flex items-center justify-between border-b border-glass-divider pb-3">
                            <span className="font-medium text-text-primary text-sm flex items-center gap-2">
                              <Database className="w-4 h-4 text-status-success" /> Autonomous Decisions Made
                              <div className="relative group/info inline-block">
                                <button type="button" className="p-0.5 text-text-muted hover:text-accent-primary transition-colors">
                                  <Info className="w-3.5 h-3.5" />
                                </button>
                                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-2.5 bg-void border border-glass-border rounded-xl shadow-2xl text-[11px] text-text-secondary opacity-0 pointer-events-none group-hover/info:opacity-100 transition-opacity z-50">
                                  Architectural choices and security policies evaluated and chosen by OrchX engine.
                                </div>
                              </div>
                            </span>
                            <span className="text-xs text-text-muted">OrchX Decision Engine</span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {msg.decisions.map((dec: any) => (
                              <div key={dec.id} className="p-3 bg-void/50 border border-glass-divider rounded-lg flex flex-col space-y-1">
                                <span className="text-[11px] font-mono text-accent-primary uppercase">{dec.title}</span>
                                <span className="text-xs font-medium text-text-primary">{dec.choice}</span>
                                <span className="text-[10px] text-text-muted">{dec.reason}</span>
                              </div>
                            ))}
                          </div>

                          <div className="border-t border-glass-divider pt-3 flex items-center space-x-3">
                            <Link href={`/workflow-forge?mission=${encodeURIComponent(msg.missionName || 'Active Mission')}`} className="flex-1 text-center py-2 bg-accent-primary text-white hover:bg-accent-hover rounded-lg text-xs font-medium transition-colors">
                              Execute Mission
                            </Link>
                            <Link href="/runtime-observatory" className="px-4 py-2 bg-surface-hover text-text-primary hover:bg-surface-active rounded-lg text-xs font-medium transition-colors border border-glass-border">
                              Inspect Decision Log
                            </Link>
                          </div>
                        </div>
                      )}
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
