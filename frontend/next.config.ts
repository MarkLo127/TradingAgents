import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactCompiler: true,
  async rewrites() {
    // In development: use localhost backend
    // In production (Railway): use BACKEND_URL env var or fallback to Railway URL
    const isDev = process.env.NODE_ENV === 'development';
    // Default to http://backend:8000 in production (Docker) if not set
    const backendUrl = process.env.BACKEND_URL || 
      (isDev ? "http://localhost:8000" : "http://backend:8000");
    
    console.log(`[Next.js] Rewriting API requests to: ${backendUrl}`);
    
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
