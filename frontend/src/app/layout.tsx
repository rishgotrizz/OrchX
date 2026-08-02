import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono" });

import { ReactQueryProvider } from "@/app/providers";
import { BackgroundManager } from "@/components/experience/BackgroundManager";
import { RootErrorBoundary } from "@/components/core/RootErrorBoundary";

export const metadata: Metadata = {
  title: "OrchX | AI Operating System Control Console",
  description: "Unified control console for orchestrating AI providers, agents, tools, workflows, and workspace memory.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <body>
        <RootErrorBoundary>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            <ReactQueryProvider>
              <BackgroundManager />
              {children}
            </ReactQueryProvider>
          </ThemeProvider>
        </RootErrorBoundary>
      </body>


    </html>
  );
}
