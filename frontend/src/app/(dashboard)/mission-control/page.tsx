"use client";

import React, { useState, useRef, useEffect } from "react";
import { MissionProvider } from "@/contexts/MissionContext";
import { useSettingsContext } from "@/contexts/SettingsContext";
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
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Closed by default when no tasks are running!
  const [showPreview, setShowPreview] = useState(false);
  const [deviceProfile, setDeviceProfile] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [activeMissionTitle, setActiveMissionTitle] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { getSettingValue } = useSettingsContext();

  // Load chat messages when URL chat ID parameter changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const chatId = params.get("chat");
      const missionName = params.get("mission");
      
      if (chatId) {
        setConversationId(chatId);
        setIsChatting(true);
        const stored = localStorage.getItem(`orchx_chat_messages_${chatId}`);
        if (stored) {
          try {
            setMessages(JSON.parse(stored));
          } catch (e) {
            setMessages([]);
          }
        } else {
          setMessages([]);
        }
        if (missionName) {
          setActiveMissionTitle(missionName);
        }
      } else {
        setConversationId(null);
        setMessages([]);
        setIsChatting(false);
        setActiveMissionTitle(null);
      }
    }
  }, [typeof window !== 'undefined' ? window.location.search : null]);

  const handleSubmit = (e?: React.FormEvent, customPrompt?: string) => {
    e?.preventDefault();
    if (loading) return;
    const textToSubmit = customPrompt || prompt;
    if (!textToSubmit.trim()) return;
    
    setIsChatting(true);
    setLoading(true);
    
    const newMsg = { role: "user", content: textToSubmit };
    const loadingMsg = { role: "assistant", content: "Thinking...", loading: true };
    const updatedUserMessages = [...messages, newMsg, loadingMsg];
    setMessages(updatedUserMessages);
    setPrompt("");

    let activeConversationId = conversationId;
    if (!activeConversationId) {
      activeConversationId = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `conv-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
      setConversationId(activeConversationId);
    }

    // Save active conversation history
    if (typeof window !== 'undefined') {
      const cleanText = textToSubmit.slice(0, 30) + (textToSubmit.length > 30 ? "..." : "");
      const existingHistory = JSON.parse(localStorage.getItem('orchx_chat_history') || '[]');
      const conversationTitle = cleanText.trim() || "New Chat";
      
      const newHistoryItem = { 
        id: activeConversationId, 
        title: conversationTitle, 
        createdAt: new Date().toISOString() 
      };
      
      const updatedHistory = [
        newHistoryItem, 
        ...existingHistory.filter((item: any) => item.id !== activeConversationId)
      ];
      localStorage.setItem('orchx_chat_history', JSON.stringify(updatedHistory));
      window.dispatchEvent(new Event('orchx_chat_updated'));
      localStorage.setItem(`orchx_chat_messages_${activeConversationId}`, JSON.stringify(updatedUserMessages.filter(m => !m.loading)));
    }

    const preferredProvider = getSettingValue("routing.default_provider");
    const preferredModel = getSettingValue("routing.primary_model");

    import('@/lib/repositories/RuntimeRepository').then(async ({ RuntimeRepository }) => {
      try {
        const res = await RuntimeRepository.executePrompt({
          prompt: textToSubmit,
          conversation_id: activeConversationId || undefined,
          provider: preferredProvider,
          model: preferredModel,
          stream: false
        });

        setMessages(prev => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].loading) {
            updated[lastIdx] = {
              role: "assistant",
              content: res.response || "",
              metadata: {
                provider: res.provider,
                model: res.model,
                latencyMs: res.latency_ms,
                requestId: res.request_id
              }
            };
          }
          if (typeof window !== 'undefined') {
            localStorage.setItem(`orchx_chat_messages_${activeConversationId}`, JSON.stringify(updated));
          }
          return updated;
        });
      } catch (err: any) {
        console.error("OrchX execution failed:", err);
        const detailMsg = err.response?.data?.detail;
        let displayMsg = "Sorry, I couldn't complete that request.";
        let errorCode = "PROVIDER_REQUEST_FAILED";
        
        if (typeof detailMsg === "string") {
          const match = detailMsg.match(/^\[([A-Z0-9_]+)\]\s*(.*)$/);
          if (match) {
            errorCode = match[1];
            const msgBody = match[2];
            if (errorCode === "NO_PROVIDER_CONFIGURED") {
              displayMsg = "No AI providers are configured yet. Please configure a provider and save its API key in Settings Studio to start executing prompts.";
            } else if (errorCode === "PROVIDER_NOT_CONFIGURED") {
              displayMsg = "The selected provider is not configured. Please add its API key in Settings Studio.";
            } else if (errorCode === "PROVIDER_AUTH_FAILED") {
              displayMsg = "Provider authentication failed. Please verify your API key in Settings Studio.";
            } else if (errorCode === "PROVIDER_UNAVAILABLE") {
              displayMsg = "This provider is temporarily unavailable. Try again or check your connectivity.";
            } else if (errorCode === "PROVIDER_TIMEOUT") {
              displayMsg = "The provider took too long to respond. Please try again.";
            } else if (errorCode === "INVALID_PROVIDER_CONFIGURATION") {
              displayMsg = "The provider configuration is invalid. Please review your settings.";
            } else {
              displayMsg = msgBody;
            }
          } else {
            displayMsg = detailMsg.replace("Execution error: ", "");
          }
        }
        setMessages(prev => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].loading) {
            updated[lastIdx] = {
              role: "assistant",
              content: displayMsg,
              error: true,
              metadata: {
                requestId: err.response?.data?.request_id || "unknown"
              }
            };
          }
          if (typeof window !== 'undefined') {
            localStorage.setItem(`orchx_chat_messages_${activeConversationId}`, JSON.stringify(updated));
          }
          return updated;
        });
      } finally {
        setLoading(false);
      }
    });
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
                          {msg.loading ? (
                            <div className="flex items-center space-x-2 text-text-muted text-xs font-medium animate-pulse py-2">
                              <Sparkles className="w-3.5 h-3.5 text-accent-primary animate-spin" />
                              <span>Thinking...</span>
                            </div>
                          ) : (
                            <div className="text-text-primary text-sm leading-relaxed whitespace-pre-wrap">
                              {msg.content}
                            </div>
                          )}

                          {/* Metadata Details Footnote */}
                          {!msg.loading && msg.metadata && (
                            <div className="text-[10px] text-text-muted flex items-center space-x-3 border-t border-glass-divider pt-1.5 w-fit">
                              {msg.metadata.provider && (
                                <span>Provider: <strong className="text-text-secondary">{msg.metadata.provider}</strong></span>
                              )}
                              {msg.metadata.model && (
                                <span>Model: <strong className="text-text-secondary">{msg.metadata.model}</strong></span>
                              )}
                              {msg.metadata.latencyMs !== undefined && (
                                <span>Latency: <strong className="text-text-secondary">{msg.metadata.latencyMs}ms</strong></span>
                              )}
                              {msg.metadata.requestId && (
                                <span>ID: <strong className="text-text-secondary">{msg.metadata.requestId}</strong></span>
                              )}
                            </div>
                          )}
                          
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
                    disabled={loading}
                    placeholder={loading ? "Thinking..." : "Ask OrchX to build..."}
                    className="w-full bg-transparent resize-none p-3 pb-1 focus:outline-none text-text-primary placeholder:text-text-muted text-xs leading-relaxed max-h-32 overflow-y-auto disabled:opacity-50"
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
                      disabled={!prompt.trim() || loading}
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
