import { redirect } from "next/navigation";

import { getSession } from "@/lib/auth/session";
import { SessionProvider } from "@/lib/auth/session-context";
import { AppSidebar } from "./_components/app-sidebar";
import { AppTopbar } from "./_components/app-topbar";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();
  if (!session) redirect("/login");

  return (
    <SessionProvider session={session}>
      <div className="flex min-h-dvh">
        <AppSidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <AppTopbar />
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <div className="mx-auto w-full max-w-[1600px]">{children}</div>
          </main>
        </div>
      </div>
    </SessionProvider>
  );
}
