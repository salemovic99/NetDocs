import type { Metadata } from "next";
import { Network } from "lucide-react";

import { LoginForm } from "./_components/login-form";

export const metadata: Metadata = { title: "Sign in — NetDocs" };

export default function LoginPage() {
  return (
    <div className="grid min-h-dvh lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-border bg-surface-container-lowest p-10 lg:flex">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              "radial-gradient(60rem 40rem at 20% -10%, rgba(77,142,255,0.18), transparent), radial-gradient(40rem 30rem at 90% 110%, rgba(78,222,163,0.12), transparent)",
          }}
        />
        <div className="relative flex items-center gap-2 text-on-surface">
          <div className="flex size-8 items-center justify-center rounded-md bg-primary-container text-primary-foreground">
            <Network className="size-5" />
          </div>
          <span className="text-h3">NetDocs</span>
        </div>
        <div className="relative space-y-3">
          <h2 className="max-w-md text-h1 text-on-surface">
            Your team&apos;s network &amp; IT knowledge, in one searchable place.
          </h2>
          <p className="max-w-md text-body-lg text-on-surface-variant">
            Document problems, root causes and resolutions — tied to the devices,
            sites and VLANs they affect. Find a prior fix in seconds.
          </p>
        </div>
        <p className="relative text-body-sm text-on-surface-variant">
          Self-hosted · on-premise · role-based access
        </p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm space-y-8">
          <div className="space-y-1.5">
            <h1 className="text-h1 text-on-surface">Sign in</h1>
            <p className="text-body-lg text-on-surface-variant">
              Enter your credentials to access the console.
            </p>
          </div>
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
