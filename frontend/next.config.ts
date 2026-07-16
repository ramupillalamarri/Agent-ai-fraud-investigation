import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Fixes "workspace root" warning when running from a subdirectory
  outputFileTracingRoot: path.join(__dirname, "../"),
  // Allows Replit's proxied preview iframe to load Next.js assets
  allowedDevOrigins: ["127.0.0.1", "localhost", "*.replit.dev", "*.sisko.replit.dev", "*.repl.co"],
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "avatars.githubusercontent.com",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
    ],
  },
};

export default nextConfig;
