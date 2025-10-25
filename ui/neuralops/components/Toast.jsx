import { useEffect } from 'react'

export default function Toast({ message, type = 'info', onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000)
    return () => clearTimeout(timer)
  }, [onClose])
  
  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return { background: '#10b981', color: 'white' }
      case 'error':
        return { background: '#ef4444', color: 'white' }
      case 'warning':
        return { background: '#f59e0b', color: 'white' }
      default:
        return { background: '#4f46e5', color: 'white' }
    }
  }
  
  return (
    <div style={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      padding: '1rem 1.5rem',
      borderRadius: '6px',
      zIndex: 1001,
      maxWidth: '400px',
      ...getTypeStyles()
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>{message}</span>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'inherit',
            cursor: 'pointer',
            marginLeft: '1rem',
            fontSize: '1.25rem'
          }}
        >
          ×
        </button>
      </div>
    </div>
  )
}