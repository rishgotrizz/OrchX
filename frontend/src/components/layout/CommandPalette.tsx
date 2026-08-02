"use client";

import * as React from "react";
import { Command } from "cmdk";
import { Search, Sparkles } from "lucide-react";
import { WORKSPACE_REGISTRY } from "@/lib/workspace-registry";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

export function CommandPalette({
  open,
  setOpen,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
}) {
  const router = useRouter();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(true);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [setOpen]);

  return (
    <AnimatePresence>
      {open && (
        <Command.Dialog
          open={open}
          onOpenChange={setOpen}
          className="fixed inset-0 z-50 bg-void/80 backdrop-blur-sm flex items-start justify-center pt-[15vh]"
          label="Global Command Palette"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ type: "spring", duration: 0.5, bounce: 0 }}
            className="w-full max-w-2xl bg-surface-elevated border border-glass-border rounded-xl shadow-2xl overflow-hidden flex flex-col"
          >
            <div className="flex items-center px-4 border-b border-glass-border">
              <Search className="w-5 h-5 text-text-muted mr-3" />
              <Command.Input
                placeholder="Search workspaces, commands, or jump to..."
                className="flex-1 h-14 bg-transparent text-text-primary placeholder:text-text-muted outline-none border-none focus:ring-0 text-lg"
              />
              <div className="flex items-center space-x-1 text-xs text-text-muted font-mono">
                <span className="px-1.5 py-0.5 rounded border border-glass-border bg-surface">ESC</span>
                <span>to close</span>
              </div>
            </div>

            <Command.List className="max-h-[60vh] overflow-y-auto p-2 scroll-smooth">
              <Command.Empty className="py-10 text-center text-text-secondary text-sm">
                No results found.
              </Command.Empty>

              <Command.Group heading="Recent Workspaces" className="px-2 py-2 text-xs font-semibold text-text-muted tracking-wider uppercase mb-1">
                {WORKSPACE_REGISTRY.slice(0, 3).map((ws) => (
                  <Command.Item
                    key={ws.id}
                    onSelect={() => {
                      router.push(ws.route);
                      setOpen(false);
                    }}
                    className="flex items-center px-3 py-3 rounded-md text-sm text-text-secondary aria-selected:bg-surface-hover aria-selected:text-text-primary cursor-pointer transition-colors group"
                  >
                    <ws.icon className="w-4 h-4 mr-3 stroke-[1.5]" />
                    <span className="flex-1">{ws.title}</span>
                    <span className="font-mono text-xs text-text-muted opacity-0 group-aria-selected:opacity-100 transition-opacity">
                      {ws.shortcut}
                    </span>
                  </Command.Item>
                ))}
              </Command.Group>

              <div className="h-px w-full bg-glass-divider my-1" />

              <Command.Group heading="Available Workspaces" className="px-2 py-2 text-xs font-semibold text-text-muted tracking-wider uppercase mb-1">
                {WORKSPACE_REGISTRY.slice(3).map((ws) => (
                  <Command.Item
                    key={ws.id}
                    onSelect={() => {
                      router.push(ws.route);
                      setOpen(false);
                    }}
                    className="flex items-center px-3 py-3 rounded-md text-sm text-text-secondary aria-selected:bg-surface-hover aria-selected:text-text-primary cursor-pointer transition-colors group"
                  >
                    <ws.icon className="w-4 h-4 mr-3 stroke-[1.5]" />
                    <span className="flex-1">{ws.title}</span>
                    <span className="font-mono text-xs text-text-muted opacity-0 group-aria-selected:opacity-100 transition-opacity">
                      {ws.shortcut}
                    </span>
                  </Command.Item>
                ))}
              </Command.Group>

              <div className="h-px w-full bg-glass-divider my-1" />

              <Command.Group heading="Quick Actions" className="px-2 py-2 text-xs font-semibold text-text-muted tracking-wider uppercase mb-1">
                <Command.Item className="flex items-center px-3 py-3 rounded-md text-sm text-accent-primary aria-selected:bg-accent-primary/10 aria-selected:text-accent-primary cursor-pointer transition-colors">
                  <Sparkles className="w-4 h-4 mr-3 stroke-[1.5]" />
                  <span>Create new AI workflow</span>
                </Command.Item>
              </Command.Group>
            </Command.List>
          </motion.div>
        </Command.Dialog>
      )}
    </AnimatePresence>
  );
}
