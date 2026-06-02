import type { Metadata } from "next";
import { Suspense } from "react";

import { PageHeader } from "@/components/shared/page-header";
import { SearchResults } from "./_components/search-results";

export const metadata: Metadata = { title: "Search — NetDocs" };

export default function SearchPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Search"
        description="Full-text search across problems and inventory."
      />
      <Suspense>
        <SearchResults />
      </Suspense>
    </div>
  );
}
