import * as React from "react"
import { LucideIcon } from "lucide-react"
import { motion } from "framer-motion"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center h-full min-h-[300px]">
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className="w-16 h-16 rounded-2xl bg-surface-active border border-glass-border flex items-center justify-center mb-6 shadow-glow relative"
      >
        <div className="absolute inset-0 bg-accent-primary/20 blur-xl rounded-full mix-blend-screen" />
        <Icon className="h-8 w-8 text-accent-primary stroke-[1.5] relative z-10" />
      </motion.div>
      <h3 className="text-xl font-bold text-text-primary mb-2 tracking-tight">{title}</h3>
      <p className="text-sm text-text-secondary max-w-sm mb-8 leading-relaxed">{description}</p>
      {action}
    </div>
  )
}
