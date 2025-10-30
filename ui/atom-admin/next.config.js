/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: false
  },
  env: {
    ATOM_APP_NAME: 'ATOM Admin Console',
    ATOM_VERSION: '1.0.0'
  },
  async rewrites() {
    return [
      {
        source: '/atom/:path*',
        destination: '/atom/:path*'
      }
    ]
  }
}

module.exports = nextConfig