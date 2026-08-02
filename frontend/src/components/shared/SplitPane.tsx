"use client";

import * as React from "react"
import { cn } from "@/lib/utils"

interface SplitPaneProps extends React.HTMLAttributes<HTMLDivElement> {
  left: React.ReactNode
  right: React.ReactNode
  defaultSplit?: number // percentage 0-100
}

export function SplitPane({ left, right, defaultSplit = 50, className, ...props }: SplitPaneProps) {
  const [split, setSplit] = React.useState(defaultSplit)
  const isDragging = React.useRef(false)

  const handleMouseDown = React.useCallback(() => {
    isDragging.current = true
    document.body.style.cursor = 'col-resize'
  }, [])

  const handleMouseUp = React.useCallback(() => {
    isDragging.current = false
    document.body.style.cursor = 'default'
  }, [])

  const handleMouseMove = React.useCallback((e: MouseEvent) => {
    if (!isDragging.current) return
    const newSplit = (e.clientX / window.innerWidth) * 100
    if (newSplit > 20 && newSplit < 80) {
      setSplit(newSplit)
    }
  }, [])

  React.useEffect(() => {
    document.addEventListener("mousemove", handleMouseMove)
    document.addEventListener("mouseup", handleMouseUp)
    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  return (
    <div className={cn("flex w-full h-full relative", className)} {...props}>
      <div style={{ width: `${split}%` }} className="h-full overflow-hidden">
        {left}
      </div>
      <div
        className="w-1 h-full bg-transparent hover:bg-accent-primary/50 cursor-col-resize transition-colors z-10 flex-shrink-0 relative -ml-[2px]"
        onMouseDown={handleMouseDown}
      />
      <div style={{ width: `${100 - split}%` }} className="h-full overflow-hidden">
        {right}
      </div>
    </div>
  )
}
