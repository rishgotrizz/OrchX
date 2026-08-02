import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-micro font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2 uppercase tracking-widest",
  {
    variants: {
      variant: {
        default:
          "bg-surface text-text-primary",
        healthy:
          "bg-status-healthy/10 text-status-healthy",
        warning:
          "bg-status-warning/10 text-status-warning",
        error:
          "bg-status-error/10 text-status-error",
        outline: "text-text-primary border border-glass-border bg-transparent",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
