"use client";

import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/core/Button";
import { Card } from "@/components/core/Card";
import { PageTransition } from "@/components/shared/PageTransition";

export default function Login() {
  const { loading } = useAuth(); // using isolated auth hook
  return (
    <PageTransition>
      <div className="min-h-screen bg-void flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8">
          <div className="flex flex-col items-center space-y-6">
            <h1 className="text-3xl font-extrabold text-gradient">OrchX</h1>
            <p className="text-text-secondary text-sm">Authenticate to access Kernel workspace</p>
            <div className="w-full space-y-4">
              <input type="email" placeholder="Email" className="w-full h-10 px-3 rounded-md bg-void border border-glass-border focus:border-accent-primary focus:ring-1 focus:ring-accent-primary text-sm outline-none transition-colors" />
              <input type="password" placeholder="Password" className="w-full h-10 px-3 rounded-md bg-void border border-glass-border focus:border-accent-primary focus:ring-1 focus:ring-accent-primary text-sm outline-none transition-colors" />
              <Button className="w-full mt-2" variant="primary">Sign In</Button>
            </div>
          </div>
        </Card>
      </div>
    </PageTransition>
  )
}
