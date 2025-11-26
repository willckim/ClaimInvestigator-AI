/** @type {import('next').NextConfig} */

const isDev = process.env.NODE_ENV !== 'production';

const nextConfig = {
  reactStrictMode: true,

  // Only proxy API requests to localhost in DEVELOPMENT
  async rewrites() {
    if (!isDev) return [];

    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Environment variable exposed to browser
  env: {
    // If Vercel has NEXT_PUBLIC_API_URL set, use that.
    // Otherwise, default to localhost for dev.
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;
