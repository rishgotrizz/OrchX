"use client";

import { motion } from "framer-motion";
import { Dock } from "@/components/layout/Dock";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { Inspector } from "@/components/shared/Inspector";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { WORKSPACE_REGISTRY } from "@/lib/workspace-registry";
import { useUiStore } from "@/stores/uiStore";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [cmdOpen, setCmdOpen] = useState(false);
  const router = useRouter();
  const toggleInspector = useUiStore((state) => state.toggleInspector);

  // Global Keyboard Navigation (⌘1-7, ⌘\)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if inside an input
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;
      
      if (e.metaKey || e.ctrlKey) {
        if (e.key === '\\') {
          e.preventDefault();
          toggleInspector();
          return;
        }

        const numKey = parseInt(e.key);
        if (!isNaN(numKey) && numKey >= 1 && numKey <= 7) {
          e.preventDefault();
          const shortcut = `⌘${numKey}`;
          const target = WORKSPACE_REGISTRY.find(w => w.shortcut === shortcut);
          if (target) {
            router.push(target.route);
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [router, toggleInspector]);

  return (
    <div className="h-screen w-screen bg-void text-text-primary overflow-hidden flex flex-col font-sans">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:p-4 focus:bg-accent-primary focus:text-white top-0 left-0 rounded-br-lg font-medium outline-none">
        Skip to main content
      </a>
      <CommandPalette open={cmdOpen} setOpen={setCmdOpen} />
      
      <div className="flex flex-1 relative">
        <motion.div
          initial={{ x: -256, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.4, ease: "easeOut" }}
        >
          <Dock />
        </motion.div>

        <motion.main 
          id="main-content"
          className="flex-1 ml-64 relative bg-void overflow-hidden flex"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4, ease: "easeOut" }}
        >
          <div className="flex-1 relative overflow-hidden">
            {children}
          </div>
          <Inspector />
        </motion.main>
      </div>
    </div>
  );
}
