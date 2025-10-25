/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_BASE: process.env.API_BASE || 'http://localhost:8080',
    ORCHESTRATOR_URL: process.env.ORCHESTRATOR_URL || 'http://localhost:8004',
    RECOMMENDER_URL: process.env.RECOMMENDER_URL || 'http://localhost:8003',
    AUTH_PUBLIC_KEY: process.env.AUTH_PUBLIC_KEY || 'mock-key'
  }
}

module.exports = nextConfig