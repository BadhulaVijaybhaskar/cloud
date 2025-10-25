import Link from 'next/link'
import { useRouter } from 'next/router'
import React from 'react'

export default function Header() {
  const router = useRouter()
  
  const isActive = (path) => router.pathname === path
  
  return React.createElement(
    'header',
    { className: 'header' },
    React.createElement(
      'div',
      { className: 'container' },
      React.createElement(
        'nav',
        { className: 'nav' },
        React.createElement(
          Link,
          { href: '/', className: 'logo' },
          '⚛️ NeuralOps'
        ),
        React.createElement(
          'div',
          { className: 'nav-links' },
          React.createElement(
            Link,
            { href: '/dashboard', className: `nav-link ${isActive('/dashboard') ? 'active' : ''}` },
            'Dashboard'
          ),
          React.createElement(
            Link,
            { href: '/playbooks', className: `nav-link ${isActive('/playbooks') ? 'active' : ''}` },
            'Playbooks'
          ),
          React.createElement(
            Link,
            { href: '/onboard', className: `nav-link ${isActive('/onboard') ? 'active' : ''}` },
            'Onboard'
          ),
          React.createElement(
            Link,
            { href: '/settings', className: `nav-link ${isActive('/settings') ? 'active' : ''}` },
            'Settings'
          )
        )
      )
    )
  )
}