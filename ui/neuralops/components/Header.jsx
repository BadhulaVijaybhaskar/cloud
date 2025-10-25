import Link from 'next/link'
import { useRouter } from 'next/router'

export default function Header() {
  const router = useRouter()
  
  const isActive = (path) => router.pathname === path
  
  return (
    <header className="header">
      <div className="container">
        <nav className="nav">
          <Link href="/" className="logo">
            ⚛️ NeuralOps
          </Link>
          
          <div className="nav-links">
            <Link href="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}>
              Dashboard
            </Link>
            <Link href="/playbooks" className={`nav-link ${isActive('/playbooks') ? 'active' : ''}`}>
              Playbooks
            </Link>
            <Link href="/onboard" className={`nav-link ${isActive('/onboard') ? 'active' : ''}`}>
              Onboard
            </Link>
            <Link href="/settings" className={`nav-link ${isActive('/settings') ? 'active' : ''}`}>
              Settings
            </Link>
          </div>
        </nav>
      </div>
    </header>
  )
}