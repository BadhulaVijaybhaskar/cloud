import { useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import Button from '../components/Button';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Demo mode - bypass auth
    setTimeout(() => {
      localStorage.setItem('token', 'demo-token');
      router.push('/dashboard');
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="3" fill="white" />
              <g stroke="rgba(255,255,255,0.8)" strokeWidth="1.5" strokeLinecap="round">
                <ellipse cx="12" cy="12" rx="8" ry="3" />
                <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(60 12 12)" />
                <ellipse cx="12" cy="12" rx="8" ry="3" transform="rotate(120 12 12)" />
              </g>
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">ATOM</h2>
          <p className="mt-2 text-sm text-gray-600">Adaptive Topology Orchestration Module</p>
          <p className="mt-1 text-xs text-gray-500">Sign in to your admin account</p>
        </div>
        
        <form className="mt-8 space-y-6 bg-white p-8 rounded-xl shadow-lg" onSubmit={handleLogin}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your email"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <Button type="submit" loading={loading} className="w-full" size="lg">
            Sign in
          </Button>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Demo credentials: admin@atom.local / password
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
