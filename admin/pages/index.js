import React from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();
  
  React.useEffect(() => {
    router.push('/dashboard');
  }, [router]);

  return React.createElement('div', { 
    style: { 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontFamily: 'system-ui'
    }
  },
    React.createElement('div', { style: { textAlign: 'center' } },
      React.createElement('h1', null, '⚡ ATOM Cloud'),
      React.createElement('p', null, 'Redirecting to dashboard...')
    )
  );
}