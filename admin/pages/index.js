import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:9999/auth/login', { email, password });
      setToken(res.data.token);
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded shadow-md w-96">
        <h1 className="text-2xl font-bold mb-4">Naksha Cloud Admin</h1>
        {!token ? (
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border mb-2"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border mb-4"
            />
            <button onClick={handleLogin} className="w-full bg-blue-500 text-white p-2 rounded">
              Login
            </button>
          </div>
        ) : (
          <div>
            <p>Logged in! Token: {token.substring(0, 20)}...</p>
            <a href="/launchpad" className="block mt-4 bg-green-500 text-white p-2 rounded text-center">
              Go to Launchpad
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
