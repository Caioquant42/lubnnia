/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { 
    unoptimized: false 
  },
  
  // Add cache headers for better cache control
  async headers() {
    return [
      {
        // Apply cache headers to all pages
        source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
          {
            key: 'Pragma',
            value: 'no-cache',
          },
          {
            key: 'Expires',
            value: '0',
          },
        ],
      },
      {
        // Cache static assets with versioning
        source: '/_next/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Cache images with shorter cache time
        source: '/_next/image/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400', // 1 day
          },
        ],
      },
      {
        // Cache favicon
        source: '/favicon.ico',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400', // 1 day
          },
        ],
      },
    ];
  },
  
  // Only use API rewrites in development to avoid CORS issues
  async rewrites() {
    // Only rewrite in development - in production, use relative URLs that go through Nginx
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://127.0.0.1:5000/api/:path*',
        },
      ];
    }
    return [];
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
// For development server configuration
if (process.env.NODE_ENV === 'development') {
  module.exports = {
    ...nextConfig,
    serverOptions: {
      hostname: '0.0.0.0',
      port: 3000,
    },
  };
}
