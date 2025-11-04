import { useState } from 'react'
import { useRouter } from 'next/router'
import Layout from '../components/Layout'

export default function Checkout() {
  const router = useRouter()
  const { model } = router.query
  const [processing, setProcessing] = useState(false)
  const [completed, setCompleted] = useState(false)

  const handlePurchase = async () => {
    setProcessing(true)
    
    setTimeout(() => {
      setProcessing(false)
      setCompleted(true)
    }, 2000)
  }

  if (completed) {
    return (
      <Layout title="Purchase Complete - ATOM Marketplace">
        <div className="min-h-screen flex items-center justify-center">
          <div className="quantum-card p-8 text-center max-w-md">
            <div className="text-6xl mb-4 text-emerald-500">✓</div>
            <h2 className="text-2xl font-bold neural-text mb-4">Purchase Complete!</h2>
            <p className="text-muted-foreground mb-6">
              Your model has been deployed to your project.
            </p>
            <div className="p-4 bg-secondary/20 rounded-lg mb-6">
              <div className="text-sm font-medium mb-2">License Token:</div>
              <div className="font-mono text-xs bg-background p-2 rounded border">
                lic_**********************abc123
              </div>
            </div>
            <button 
              onClick={() => router.push('/project/p-1')}
              className="atom-gradient text-white px-6 py-3 rounded-lg font-medium"
            >
              View in Project
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Checkout - ATOM Marketplace">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold neural-text mb-8">Checkout</h1>
        
        <div className="quantum-card p-8">
          <h2 className="text-xl font-bold mb-6">Order Summary</h2>
          
          <div className="border-b border-border pb-4 mb-4">
            <div className="flex justify-between items-center">
              <div>
                <div className="font-medium">ATOM Neural Optimizer</div>
                <div className="text-sm text-muted-foreground">Monthly subscription</div>
              </div>
              <div className="font-bold">$29.99</div>
            </div>
          </div>

          <div className="flex justify-between items-center text-lg font-bold mb-6">
            <span>Total</span>
            <span>$29.99/month</span>
          </div>

          <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <h3 className="font-semibold text-blue-600 mb-2">License Agreement</h3>
            <p className="text-sm text-muted-foreground">
              By purchasing, you agree to the MIT license terms and ATOM marketplace policies.
            </p>
          </div>

          <button 
            onClick={handlePurchase}
            disabled={processing}
            className="w-full atom-gradient text-white py-3 px-6 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
          >
            {processing ? 'Processing...' : 'Complete Purchase'}
          </button>
        </div>
      </div>
    </Layout>
  )
}