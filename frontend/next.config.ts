import type { NextConfig } from "next";
import bundleAnalyzer from "@next/bundle-analyzer";
import { execSync } from "child_process";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

let commitSha = "UNKNOWN";
try {
  commitSha = execSync("git rev-parse --short HEAD").toString().trim();
} catch (e) {
  // Fallback if git is not available
}

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_BUILD_COMMIT_SHA: commitSha,
  },
  // eslint config is handled in eslint.config.mjs
  typescript: {
    ignoreBuildErrors: true,
  },
  turbopack: {
    root: __dirname,
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
};

export default withBundleAnalyzer(nextConfig);
