/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        background: 'var(--bg)',
        surface1: 'var(--surface-1)',
        surface2: 'var(--surface-2)',
        textPrimary: 'var(--text-primary)',
        textMuted: 'var(--text-muted)',
        brandA: 'var(--brand-a)',
        brandB: 'var(--brand-b)',
        'atom-border': 'var(--atom-border)',
        'atom-hover': 'var(--atom-hover)',
        'atom-success': 'var(--atom-success)',
        'atom-warning': 'var(--atom-warning)',
        'atom-error': 'var(--atom-error)',
        'atom-info': 'var(--atom-info)',
        atom: {
          primary: 'var(--brand-a)',
          secondary: 'var(--brand-b)',
          gradient: 'var(--cta-gradient)'
        }
      },
      backgroundImage: {
        'atom-gradient': 'var(--cta-gradient)',
        'cta-gradient': 'var(--cta-gradient)'
      },
      borderRadius: {
        md: 'var(--radius-md)'
      },
      boxShadow: {
        soft: 'var(--shadow-1)',
        atom: 'var(--shadow-1)'
      },
      fontFamily: {
        sans: ['var(--font-ui)', 'Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif']
      },
      animation: {
        'atom-pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'atom-fade-in': 'fadeIn 0.5s ease-in-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      }
    }
  },
  plugins: []
}