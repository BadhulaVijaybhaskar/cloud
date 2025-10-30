import React from 'react'
import { LucideIcon } from 'lucide-react'

interface AtomButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  icon?: LucideIcon
  iconPosition?: 'left' | 'right'
  disabled?: boolean
  loading?: boolean
  className?: string
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

export function AtomButton({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  disabled = false,
  loading = false,
  className = '',
  onClick,
  type = 'button'
}: AtomButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg atom-transition atom-focus-ring disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variantClasses = {
    primary: 'bg-atom-gradient text-white hover:shadow-lg hover:-translate-y-0.5',
    secondary: 'bg-surface1 text-textPrimary border border-atom-border hover:bg-atom-hover',
    outline: 'border-2 border-brandA text-brandA hover:bg-brandA hover:text-white',
    ghost: 'text-textMuted hover:text-textPrimary hover:bg-atom-hover',
    danger: 'bg-atom-error text-white hover:bg-red-600'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm gap-1.5',
    md: 'px-4 py-2 text-base gap-2',
    lg: 'px-6 py-3 text-lg gap-3'
  }

  const iconSize = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {loading && (
        <svg className={`animate-spin ${iconSize[size]}`} fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      
      {Icon && !loading && iconPosition === 'left' && (
        <Icon className={iconSize[size]} />
      )}
      
      <span>{children}</span>
      
      {Icon && !loading && iconPosition === 'right' && (
        <Icon className={iconSize[size]} />
      )}
    </button>
  )
}

export default AtomButton