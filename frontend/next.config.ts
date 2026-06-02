import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // The browser talks only to same-origin Next routes (BFF); the server reaches
  // the FastAPI backend via API_INTERNAL_URL. No NEXT_PUBLIC API URL is exposed.
};

export default nextConfig;
