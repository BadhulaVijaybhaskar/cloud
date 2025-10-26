/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: false,
  },
  images: {
    domains: ['localhost'],
    unoptimized: true
  },
  env: {
    ATOM_VERSION: '6.0.0-phaseF',
    NEURAL_ENGINE: 'active',
    QUANTUM_SAFE: 'enabled'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3000/api/:path*'
      }
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  }
};

module.exports = nextConfig;