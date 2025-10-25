// Simple smoke test for NeuralOps UI
const http = require('http')

const testEndpoint = async (url, description) => {
  return new Promise((resolve) => {
    const request = http.get(url, (res) => {
      console.log(`✅ ${description}: ${res.statusCode}`)
      resolve({ success: res.statusCode === 200, status: res.statusCode })
    })
    
    request.on('error', (err) => {
      console.log(`❌ ${description}: ${err.message}`)
      resolve({ success: false, error: err.message })
    })
    
    request.setTimeout(5000, () => {
      console.log(`⏰ ${description}: Timeout`)
      request.destroy()
      resolve({ success: false, error: 'Timeout' })
    })
  })
}

const runSmokeTests = async () => {
  console.log('🧪 Running NeuralOps UI Smoke Tests...\n')
  
  const tests = [
    { url: 'http://localhost:3001', description: 'Landing Page' },
    { url: 'http://localhost:3001/dashboard', description: 'Dashboard Page' },
    { url: 'http://localhost:3001/playbooks', description: 'Playbooks Page' },
    { url: 'http://localhost:3001/onboard', description: 'Onboard Page' },
    { url: 'http://localhost:3001/settings', description: 'Settings Page' },
    { url: 'http://localhost:8080/api/mock/incidents', description: 'Mock API - Incidents' },
    { url: 'http://localhost:8080/api/mock/playbooks', description: 'Mock API - Playbooks' }
  ]
  
  const results = []
  
  for (const test of tests) {
    const result = await testEndpoint(test.url, test.description)
    results.push({ ...test, ...result })
  }
  
  console.log('\n📊 Test Results Summary:')
  const passed = results.filter(r => r.success).length
  const total = results.length
  
  console.log(`Passed: ${passed}/${total}`)
  
  if (passed === total) {
    console.log('🎉 All smoke tests passed!')
    process.exit(0)
  } else {
    console.log('⚠️  Some tests failed - this may be expected if services are not running')
    console.log('Failed tests:')
    results.filter(r => !r.success).forEach(r => {
      console.log(`  - ${r.description}: ${r.error || r.status}`)
    })
    process.exit(1)
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runSmokeTests().catch(console.error)
}

module.exports = { runSmokeTests, testEndpoint }