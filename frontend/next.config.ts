import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";
const repoBasePath = process.env.NEXT_PUBLIC_BASE_PATH || (isProd ? "/concrete-gridiron" : "");

const nextConfig: NextConfig = {
  output: "export",
  basePath: repoBasePath,
  assetPrefix: repoBasePath ? `${repoBasePath}/` : undefined,
  trailingSlash: true,
  reactStrictMode: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
