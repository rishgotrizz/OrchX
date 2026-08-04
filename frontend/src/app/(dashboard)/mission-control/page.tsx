"use client";

import React, { useState, useRef, useEffect } from "react";
import { MissionProvider } from "@/contexts/MissionContext";
import { 
  Paperclip, 
  Mic, 
  ArrowUp, 
  ChevronDown, 
  FileText, 
  Database, 
  Box, 
  Info, 
  MonitorPlay, 
  Columns, 
  Maximize2, 
  Smartphone, 
  Tablet, 
  Monitor, 
  Sparkles, 
  ExternalLink,
  RotateCw,
  Code,
  X,
  Workflow
} from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

export default function MissionControlPage() {
  const [prompt, setPrompt] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  
  // Closed by default when no tasks are running!
  const [showPreview, setShowPreview] = useState(false);
  const [deviceProfile, setDeviceProfile] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [activeMissionTitle, setActiveMissionTitle] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e?: React.FormEvent, customPrompt?: string) => {
    e?.preventDefault();
    const textToSubmit = customPrompt || prompt;
    if (!textToSubmit.trim()) return;
    
    setIsChatting(true);
    const newMsg = { role: "user", content: textToSubmit };
    setMessages(prev => [...prev, newMsg]);
    setPrompt("");

    const cleanText = textToSubmit
      .replace(/^i (wanna|want to|would like to) (build|create|make)/i, '')
      .replace(/^(build|create|make)/i, '')
      .trim();

    const titleSubject = cleanText 
      ? cleanText.charAt(0).toUpperCase() + cleanText.slice(1) 
      : textToSubmit.trim();

    setActiveMissionTitle(titleSubject);
    setShowPreview(true); // Open live preview when task is run!

    // Save active mission & history
    if (typeof window !== 'undefined') {
      localStorage.setItem('orchx_active_mission', titleSubject);

      const existingHistory = JSON.parse(localStorage.getItem('orchx_chat_history') || '[]');
      const newHistoryItem = { id: `chat-${Date.now()}`, title: titleSubject, createdAt: new Date().toISOString() };
      const updatedHistory = [newHistoryItem, ...existingHistory.filter((item: any) => item.title !== titleSubject)];
      localStorage.setItem('orchx_chat_history', JSON.stringify(updatedHistory));
      window.dispatchEvent(new Event('orchx_chat_updated'));
    }

    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: `I've analyzed your request and initialized a side-by-side agent execution and live project sandbox for ${titleSubject}.`,
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

  const frameWidths = {
    desktop: 'w-full h-full border-none rounded-none',
    tablet: 'w-[768px] h-[90%] border border-glass-border rounded-xl shadow-2xl my-auto',
    mobile: 'w-[375px] h-[90%] border border-glass-border rounded-2xl shadow-2xl my-auto'
  };

  return (
    <MissionProvider>
      <div className="flex flex-col h-full bg-void overflow-hidden">
        
        {/* Top Split View Bar */}
        <div className="px-6 py-3 border-b border-glass-border flex items-center justify-between bg-surface shrink-0 z-20">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-bold text-text-primary flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-accent-primary" />
              <span>Mission Control</span>
              {activeMissionTitle && (
                <span className="text-xs px-2 py-0.5 rounded bg-accent-primary/10 text-accent-primary font-mono font-medium">
                  {activeMissionTitle}
                </span>
              )}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-void p-1 rounded-lg border border-glass-border">
              <button
                onClick={() => setShowPreview(true)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${showPreview ? 'bg-accent-primary text-white shadow-glow' : 'text-text-muted hover:text-text-primary'}`}
              >
                <Columns className="w-3.5 h-3.5" />
                <span>Side-by-Side Preview</span>
              </button>
              <button
                onClick={() => setShowPreview(false)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${!showPreview ? 'bg-accent-primary text-white shadow-glow' : 'text-text-muted hover:text-text-primary'}`}
              >
                <Maximize2 className="w-3.5 h-3.5" />
                <span>Focus Chat</span>
              </button>
            </div>

            {/* Device Profile Switcher */}
            {showPreview && (
              <div className="flex items-center space-x-1 bg-void p-1 rounded-lg border border-glass-border">
                <button
                  onClick={() => setDeviceProfile('desktop')}
                  className={`p-1 rounded text-xs transition-colors ${deviceProfile === 'desktop' ? 'bg-surface-hover text-accent-primary' : 'text-text-muted hover:text-text-primary'}`}
                  title="Desktop View"
                >
                  <Monitor className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setDeviceProfile('tablet')}
                  className={`p-1 rounded text-xs transition-colors ${deviceProfile === 'tablet' ? 'bg-surface-hover text-accent-primary' : 'text-text-muted hover:text-text-primary'}`}
                  title="Tablet View"
                >
                  <Tablet className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setDeviceProfile('mobile')}
                  className={`p-1 rounded text-xs transition-colors ${deviceProfile === 'mobile' ? 'bg-surface-hover text-accent-primary' : 'text-text-muted hover:text-text-primary'}`}
                  title="Mobile View"
                >
                  <Smartphone className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Dual Panel Workspace */}
        <div className="flex-1 flex overflow-hidden relative">
          
          {/* Left Panel: Chat & Action Plans */}
          <div className={`${showPreview ? 'w-1/2 border-r border-glass-border' : 'w-full'} flex flex-col h-full bg-void transition-all duration-300 relative`}>
            
            <div className="flex-1 overflow-y-auto px-6 py-6 pb-36">
              {!isChatting ? (
                /* Welcome Screen */
                <div className="h-full flex flex-col items-center justify-center max-w-xl mx-auto text-center space-y-8">
                  <div className="p-4 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary shadow-glow">
                    <Sparkles className="w-8 h-8" />
                  </div>
                  <div className="space-y-2">
                    <h1 className="text-2xl font-bold tracking-tight text-text-primary">What would you like to build today?</h1>
                    <p className="text-xs text-text-muted">Type any project goal to start agent execution and open live preview generation.</p>
                  </div>
                </div>
              ) : (
                /* Active Thread */
                <div className="space-y-6">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      {msg.role === 'user' ? (
                        <div className="bg-surface-active px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-[85%] text-text-primary text-sm leading-relaxed">
                          {msg.content}
                        </div>
                      ) : (
                        <div className="flex flex-col space-y-4 max-w-full w-full">
                          <div className="text-text-primary text-sm leading-relaxed">
                            {msg.content}
                          </div>
                          
                          {/* Task Plan */}
                          {msg.tasks && (
                            <div className="bg-surface border border-glass-border rounded-xl p-4 flex flex-col space-y-3 shadow-lg">
                              <div className="flex items-center justify-between border-b border-glass-divider pb-2">
                                <span className="font-semibold text-text-primary text-xs flex items-center gap-1.5">
                                  <Box className="w-3.5 h-3.5 text-accent-primary" /> Autonomous Action Plan
                                </span>
                                <span className="text-[10px] px-2 py-0.5 rounded bg-accent-primary/10 text-accent-primary font-mono uppercase">
                                  {msg.missionName || 'Active'}
                                </span>
                              </div>

                              <div className="flex flex-col space-y-2">
                                {msg.tasks.map((task: any) => (
                                  <div key={task.id} className="flex items-start justify-between p-2 bg-void/50 border border-glass-divider rounded-lg text-xs">
                                    <div className="flex flex-col">
                                      <span className="font-medium text-text-primary">{task.name}</span>
                                      <span className="text-[10px] text-text-muted">{task.detail}</span>
                                    </div>
                                    <span className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded shrink-0 ${
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

                          {/* Decision Ledger */}
                          {msg.decisions && (
                            <div className="bg-surface border border-glass-border rounded-xl p-4 flex flex-col space-y-3 shadow-lg">
                              <div className="flex items-center justify-between border-b border-glass-divider pb-2">
                                <span className="font-semibold text-text-primary text-xs flex items-center gap-1.5">
                                  <Database className="w-3.5 h-3.5 text-status-success" /> Decisions Ledger
                                </span>
                              </div>

                              <div className="grid grid-cols-3 gap-2">
                                {msg.decisions.map((dec: any) => (
                                  <div key={dec.id} className="p-2 bg-void/50 border border-glass-divider rounded-lg flex flex-col">
                                    <span className="text-[9px] font-mono text-accent-primary uppercase">{dec.title}</span>
                                    <span className="text-[11px] font-medium text-text-primary truncate">{dec.choice}</span>
                                  </div>
                                ))}
                              </div>

                              <div className="border-t border-glass-divider pt-2.5 flex items-center space-x-2">
                                <Link href={`/workflow-forge?mission=${encodeURIComponent(msg.missionName || 'Active Mission')}`} className="flex-1 text-center py-1.5 bg-accent-primary text-white hover:bg-accent-hover rounded-md text-xs font-medium transition-colors flex items-center justify-center space-x-1">
                                  <Workflow className="w-3.5 h-3.5" />
                                  <span>Run Workflow</span>
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

            {/* Input Bar */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-void via-void to-transparent pt-6 pb-4 px-4 flex justify-center z-10">
              <div className="w-full relative">
                <div className="bg-surface border border-glass-border rounded-xl shadow-2xl flex flex-col">
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask OrchX to build..."
                    className="w-full bg-transparent resize-none p-3 pb-1 focus:outline-none text-text-primary placeholder:text-text-muted text-xs leading-relaxed max-h-32 overflow-y-auto"
                    rows={1}
                    style={{ minHeight: '48px' }}
                  />
                  <div className="flex items-center justify-between p-2 pt-0">
                    <div className="flex items-center space-x-1">
                      <button className="p-1.5 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors">
                        <Paperclip className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1.5 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors">
                        <Mic className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <button 
                      onClick={handleSubmit}
                      disabled={!prompt.trim()}
                      className="p-1.5 bg-accent-primary text-white rounded-lg hover:bg-accent-hover transition-colors disabled:opacity-50"
                    >
                      <ArrowUp className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Right Panel: Side-by-Side Live Preview Sandbox (Only visible when user runs tasks!) */}
          {showPreview && (
            <div className="w-1/2 flex flex-col h-full bg-void-elevated p-4 overflow-hidden items-center justify-center relative">
              <div className={frameWidths[deviceProfile]}>
                
                <div className="w-full h-full bg-surface border border-glass-border rounded-xl flex flex-col overflow-hidden shadow-2xl">
                  
                  {/* Preview Title Bar with Close X Button */}
                  <div className="px-4 py-2 bg-void border-b border-glass-border flex items-center justify-between shrink-0">
                    <div className="flex items-center space-x-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-status-error/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-status-warning/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-status-success/80" />
                      <span className="text-xs font-mono text-text-muted ml-2">
                        {activeMissionTitle ? `${activeMissionTitle.toLowerCase().replace(/\s+/g, '-')}.orchx.app` : 'sandbox.orchx.app'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono text-status-success uppercase bg-status-success/10 px-2 py-0.5 rounded">
                        Live Sandbox Active
                      </span>
                      {/* Close X Button */}
                      <button
                        onClick={() => setShowPreview(false)}
                        className="p-1 text-text-muted hover:text-status-error transition-colors rounded hover:bg-surface-hover"
                        title="Close Live Preview"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Rendered Live App Preview Output (Dynamic per Goal) */}
                  <div className="flex-1 p-6 overflow-y-auto bg-void flex flex-col items-center justify-center">
                    {!activeMissionTitle ? (
                      /* Clean Empty State when no active mission */
                      <div className="flex flex-col items-center justify-center text-center space-y-3 p-6 text-text-muted">
                        <MonitorPlay className="w-8 h-8 text-accent-primary" />
                        <span className="text-sm font-semibold text-text-primary">No Active Product Running</span>
                        <span className="text-xs max-w-xs text-text-secondary">Run a project task from Mission Control to start rendering the live sandbox preview.</span>
                        <button
                          onClick={() => setShowPreview(false)}
                          className="mt-2 px-3 py-1.5 bg-surface border border-glass-border text-text-primary rounded-lg text-xs font-medium hover:bg-surface-hover transition-colors"
                        >
                          Close Preview
                        </button>
                      </div>
                    ) : (
                      /* Clean Dynamic Project Output (Zero Fake Hardcoded Rows!) */
                      <div className="w-full max-w-md p-6 bg-surface border border-glass-border rounded-2xl shadow-2xl flex flex-col space-y-5">
                        <div className="flex items-center justify-between border-b border-glass-divider pb-3">
                          <div className="flex items-center space-x-2">
                            <Sparkles className="w-4 h-4 text-accent-primary" />
                            <span className="text-sm font-bold text-text-primary">{activeMissionTitle}</span>
                          </div>
                          <span className="text-xs px-2 py-0.5 rounded bg-status-success/10 text-status-success font-mono">Build Active</span>
                        </div>

                        <div className="p-4 bg-void border border-glass-border rounded-xl flex flex-col space-y-2">
                          <span className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
                            <Workflow className="w-3.5 h-3.5 text-accent-primary" /> Live Agent Execution
                          </span>
                          <p className="text-xs text-text-muted">
                            Autonomous action plan generated for <strong className="text-text-primary">{activeMissionTitle}</strong>. Run workflow to build and test code.
                          </p>
                        </div>

                        <Link
                          href={`/workflow-forge?mission=${encodeURIComponent(activeMissionTitle)}`}
                          className="w-full py-2.5 bg-accent-primary hover:bg-accent-hover text-white font-semibold text-xs rounded-xl transition-all shadow-glow flex items-center justify-center space-x-2"
                        >
                          <Workflow className="w-3.5 h-3.5" />
                          <span>Run Project Workflow</span>
                        </Link>
                      </div>
                    )}
                  </div>

                  {/* Live Generation Console */}
                  <div className="px-4 py-2.5 bg-void border-t border-glass-border font-mono text-[10px] text-text-muted flex justify-between items-center shrink-0">
                    <span>Render Engine: WebPreview v2.1</span>
                    <span className="text-status-success">Synced with Agent</span>
                  </div>

                </div>

              </div>
            </div>
          )}

        </div>

      </div>
    </MissionProvider>
  );
}
