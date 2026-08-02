import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbSegment {
  label: string;
  href?: string;
}

export function Breadcrumbs({ segments }: { segments: BreadcrumbSegment[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center text-xs font-medium text-text-muted">
      <ol className="flex items-center space-x-1">
        <li>
          <Link href="/mission-control" className="hover:text-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary rounded px-1 flex items-center justify-center">
            <Home className="w-3.5 h-3.5 stroke-[2]" />
            <span className="sr-only">Home</span>
          </Link>
        </li>
        {segments.map((segment, index) => (
          <li key={index} className="flex items-center">
            <ChevronRight className="w-3.5 h-3.5 mx-1 opacity-50 shrink-0" />
            {segment.href ? (
              <Link 
                href={segment.href}
                className="hover:text-text-primary transition-colors truncate max-w-[150px] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary rounded px-1"
              >
                {segment.label}
              </Link>
            ) : (
              <span className="text-text-primary truncate max-w-[200px] px-1" aria-current="page">
                {segment.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
