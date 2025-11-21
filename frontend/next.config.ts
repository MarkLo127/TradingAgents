import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactCompiler: true,
  async rewrites() {
    // Use BACKEND_URL env var, or fallback to public Railway URL
    // In Railway, services cannot use simple hostnames to communicate
    const backendUrl = process.env.BACKEND_URL || "https://tradinaagents-backend.up.railway.app";
    
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
