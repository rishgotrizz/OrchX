"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { Toaster } from "sonner";

export function ThemeProvider({ children, ...props }: any) {
  return (
    <NextThemesProvider {...props}>
      {children}
      <Toaster 
        theme="dark" 
        position="bottom-right" 
        visibleToasts={3}
        toastOptions={{
          className: 'bg-void-elevated border-glass-border text-text-primary shadow-2xl font-sans',
          descriptionClassName: 'text-text-secondary font-sans',
        }}
      />
    </NextThemesProvider>
  );
}
