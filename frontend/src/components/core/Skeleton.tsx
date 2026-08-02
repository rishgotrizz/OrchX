import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-surface-hover",
        className
      )}
      {...props}
    />
  )
}

export function CardSkeleton() {
  return (
    <div className="p-4 border border-glass-border rounded-xl bg-void-elevated flex flex-col space-y-3">
      <Skeleton className="h-5 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="pt-4 flex justify-end">
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  )
}

export function TableSkeleton() {
  return (
    <div className="border border-glass-border rounded-xl bg-void-elevated w-full overflow-hidden flex flex-col">
      <div className="h-10 bg-surface border-b border-glass-border px-4 flex items-center space-x-4">
        <Skeleton className="h-4 w-8" />
        <Skeleton className="h-4 flex-1" />
        <Skeleton className="h-4 w-24" />
      </div>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-14 border-b border-glass-border last:border-b-0 px-4 flex items-center space-x-4">
          <Skeleton className="h-6 w-6 rounded" />
          <Skeleton className="h-4 flex-1" />
          <Skeleton className="h-4 w-24" />
        </div>
      ))}
    </div>
  )
}

export function ListSkeleton() {
  return (
    <div className="flex flex-col space-y-3 w-full">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="flex items-center space-x-3 p-3 border border-glass-border rounded-lg bg-void-elevated">
          <Skeleton className="h-10 w-10 rounded-full shrink-0" />
          <div className="flex flex-col space-y-2 flex-1">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function PanelSkeleton() {
  return (
    <div className="flex flex-col w-full h-full border border-glass-border rounded-xl bg-void-elevated overflow-hidden">
      <div className="h-12 border-b border-glass-border px-4 flex items-center justify-between shrink-0">
        <Skeleton className="h-5 w-32" />
        <div className="flex space-x-2">
          <Skeleton className="h-6 w-6 rounded" />
          <Skeleton className="h-6 w-6 rounded" />
        </div>
      </div>
      <div className="flex-1 p-4 flex flex-col space-y-4">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    </div>
  )
}

export function InspectorSkeleton() {
  return (
    <div className="flex flex-col w-64 h-full border-l border-glass-border bg-void-elevated overflow-hidden shrink-0">
      <div className="h-12 border-b border-glass-border px-4 flex items-center shrink-0">
        <Skeleton className="h-4 w-20" />
      </div>
      <div className="flex-1 p-4 flex flex-col space-y-6">
        <div className="flex flex-col space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-8 w-full rounded" />
        </div>
        <div className="flex flex-col space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-8 w-full rounded" />
        </div>
        <div className="flex flex-col space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-24 w-full rounded" />
        </div>
      </div>
    </div>
  )
}

export { Skeleton }
