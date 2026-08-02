"use client";
import { Skeleton } from "@/components/core/Skeleton";
import { PageTransition } from "@/components/shared/PageTransition";

export default function DashboardLoading() {
  return (
    <PageTransition>
      <div className="h-full flex flex-col p-6 space-y-6 w-full">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="flex-1 w-full rounded-lg" />
      </div>
    </PageTransition>
  )
}
