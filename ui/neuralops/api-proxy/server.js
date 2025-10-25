const http = require('http')
const httpProxy = require('http-proxy-middleware')
const express = require('express')

const app = express()

// Environment configuration
const config = {
  orchestratorUrl: process.env.ORCHESTRATOR_URL || 'http://localhost:8004',
  recommenderUrl: process.env.RECOMMENDER_URL || 'http://localhost:8003',
  insightEngineUrl: process.env.INSIGHT_ENGINE_URL || 'http://localhost:8002',
  registryUrl: process.env.REGISTRY_URL || 'http://localhost:8000',
  runtimeUrl: process.env.RUNTIME_URL || 'http://localhost:8001',
  authPublicKey: process.env.AUTH_PUBLIC_KEY || 'mock-key'
}

// Mock JWT for development
const mockJWT = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJyb2xlIjoib3JnLWFkbWluIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock'

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization')
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200)
  } else {
    next()
  }
})

app.use(express.json())

// Inject JWT for development
app.use((req, res, next) => {
  if (!req.headers.authorization) {
    req.headers.authorization = `Bearer ${mockJWT}`
  }
  next()
})

// Proxy routes
const createProxy = (target, pathRewrite = {}) => {
  return httpProxy.createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite,
    onError: (err, req, res) => {
      console.error(`Proxy error for ${req.url}:`, err.message)
      res.status(503).json({
        error: 'Service unavailable',
        message: `Backend service at ${target} is not reachable`,
        mock: true
      })
    }
  })
}

// Route mappings
app.use('/api/orchestrator', createProxy(config.orchestratorUrl, { '^/api/orchestrator': '' }))
app.use('/api/recommender', createProxy(config.recommenderUrl, { '^/api/recommender': '' }))
app.use('/api/insights', createProxy(config.insightEngineUrl, { '^/api/insights': '' }))
app.use('/api/registry', createProxy(config.registryUrl, { '^/api/registry': '' }))
app.use('/api/runtime', createProxy(config.runtimeUrl, { '^/api/runtime': '' }))

// Mock endpoints for development
app.get('/api/mock/incidents', (req, res) => {
  res.json([
    {
      id: 'inc-001',
      status: 'pending',
      playbook_id: 'restart-unhealthy',
      description: 'High CPU usage detected on production cluster',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 'inc-002', 
      status: 'completed',
      playbook_id: 'scale-deployment',
      description: 'Memory pressure on web servers',
      created_at: new Date(Date.now() - 7200000).toISOString(),
      updated_at: new Date(Date.now() - 1800000).toISOString()
    }
  ])
})

app.get('/api/mock/playbooks', (req, res) => {
  res.json([
    {
      id: 'restart-unhealthy',
      description: 'Restart unhealthy pods in deployment',
      safety_mode: 'manual',
      success_rate: 95,
      tags: ['kubernetes', 'restart', 'health']
    },
    {
      id: 'scale-deployment',
      description: 'Scale deployment based on resource usage',
      safety_mode: 'auto',
      success_rate: 88,
      tags: ['kubernetes', 'scaling', 'performance']
    }
  ])
})

const PORT = process.env.PORT || 8080

app.listen(PORT, () => {
  console.log(`API Proxy server running on port ${PORT}`)
  console.log('Backend services:')
  console.log(`  Orchestrator: ${config.orchestratorUrl}`)
  console.log(`  Recommender: ${config.recommenderUrl}`)
  console.log(`  Insight Engine: ${config.insightEngineUrl}`)
  console.log(`  Registry: ${config.registryUrl}`)
  console.log(`  Runtime: ${config.runtimeUrl}`)
})