import type { Metadata } from "next";

import { PageHeader } from "@/components/shared/page-header";
import { ChangePasswordForm } from "./_components/change-password-form";

export const metadata: Metadata = { title: "Change password — NetDocs" };

export default function ChangePasswordPage() {
  return (
    <div className="mx-auto max-w-md space-y-6">
      <PageHeader
        title="Change password"
        description="Choose a strong password (at least 12 characters)."
      />
      <ChangePasswordForm />
    </div>
  );
}
