import React, { useState, useEffect } from 'react'
import { Sun, Moon, Monitor } from 'lucide-react'

interface AtomThemeChooserProps {
  className?: string
}

export function AtomThemeChooser({ className = '' }: AtomThemeChooserProps) {
  const [theme, setTheme] = useState<'auto' | 'light' | 'dark'>('auto')

  useEffect(() => {
    // Initialize theme from localStorage or default to auto
    const savedTheme = localStorage.getItem('atom-theme') as 'auto' | 'light' | 'dark' | null
    const initialTheme = savedTheme || 'auto'
    setTheme(initialTheme)
    applyTheme(initialTheme)
  }, [])

  const applyTheme = (newTheme: 'auto' | 'light' | 'dark') => {
    const root = document.documentElement
    
    if (newTheme === 'auto') {
      root.removeAttribute('data-theme')
      localStorage.removeItem('atom-theme')
      // Apply system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        root.setAttribute('data-theme', 'dark')
      }
    } else {
      root.setAttribute('data-theme', newTheme)
      localStorage.setItem('atom-theme', newTheme)
    }
  }

  const handleThemeChange = (newTheme: 'auto' | 'light' | 'dark') => {
    setTheme(newTheme)
    applyTheme(newTheme)
  }

  const getIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun className="w-4 h-4" />
      case 'dark':
        return <Moon className="w-4 h-4" />
      default:
        return <Monitor className="w-4 h-4" />
    }
  }

  return (
    <div className={`relative ${className}`}>
      <select
        value={theme}
        onChange={(e) => handleThemeChange(e.target.value as 'auto' | 'light' | 'dark')}
        className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm pr-8 pl-10 py-2 min-w-[120px] appearance-none cursor-pointer text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="ATOM Theme Selector"
      >
        <option value="auto">Auto</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
      
      {/* Icon overlay */}
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none text-gray-500">
        {getIcon()}
      </div>
      
      {/* Dropdown arrow */}
      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none text-gray-500">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}

export default AtomThemeChooser