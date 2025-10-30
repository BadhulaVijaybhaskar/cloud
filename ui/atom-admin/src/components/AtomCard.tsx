import React from 'react'
import { LucideIcon } from 'lucide-react'

interface AtomCardProps {
  children: React.ReactNode
  className?: string
  title?: string
  subtitle?: string
  icon?: LucideIcon
  action?: React.ReactNode
  hover?: boolean
  gradient?: boolean
}

export function AtomCard({ 
  children, 
  className = '', 
  title, 
  subtitle, 
  icon: Icon,
  action,
  hover = true,
  gradient = false
}: AtomCardProps) {
  return (
    <div className={`
      atom-card
      ${hover ? 'atom-hover-lift' : ''}
      ${gradient ? 'bg-atom-gradient text-white' : ''}
      ${className}
    `}>
      {/* Header */}
      {(title || subtitle || Icon || action) && (
        <div className="p-6 pb-4 border-b border-atom-border">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              {Icon && (
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center
                  ${gradient ? 'bg-white/20' : 'bg-atom-gradient'}
                `}>
                  <Icon className={`w-5 h-5 ${gradient ? 'text-white' : 'text-white'}`} />
                </div>
              )}
              <div>
                {title && (
                  <h3 className={`font-semibold text-lg ${gradient ? 'text-white' : 'text-textPrimary'}`}>
                    {title}
                  </h3>
                )}
                {subtitle && (
                  <p className={`text-sm ${gradient ? 'text-white/80' : 'text-textMuted'}`}>
                    {subtitle}
                  </p>
                )}
              </div>
            </div>
            {action && (
              <div className="flex-shrink-0">
                {action}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-6">
        {children}
      </div>
    </div>
  )
}

export default AtomCard