/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // ATOM Brand Colors
        atom: {
          teal: {
            50: '#f0fdfa',
            100: '#ccfbf1',
            200: '#99f6e4',
            300: '#5eead4',
            400: '#2dd4bf',
            500: '#14b8a6', // Primary teal
            600: '#0d9488',
            700: '#0f766e',
            800: '#115e59',
            900: '#134e4a',
          },
          violet: {
            50: '#faf5ff',
            100: '#f3e8ff',
            200: '#e9d5ff',
            300: '#d8b4fe',
            400: '#c084fc',
            500: '#a855f7', // Primary violet
            600: '#9333ea',
            700: '#7c3aed',
            800: '#6b21a8',
            900: '#581c87',
          }
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        teal: {
          50: 'hsl(166 76% 97%)',
          100: 'hsl(167 85% 89%)',
          200: 'hsl(168 84% 78%)',
          300: 'hsl(171 77% 64%)',
          400: 'hsl(172 66% 50%)',
          500: 'hsl(180 80% 50%)',
          600: 'hsl(175 84% 32%)',
          700: 'hsl(175 77% 26%)',
          800: 'hsl(176 69% 22%)',
          900: 'hsl(176 61% 19%)',
        },
        violet: {
          50: 'hsl(270 100% 98%)',
          100: 'hsl(269 100% 95%)',
          200: 'hsl(269 100% 92%)',
          300: 'hsl(269 97% 85%)',
          400: 'hsl(270 95% 75%)',
          500: 'hsl(270 70% 60%)',
          600: 'hsl(271 81% 56%)',
          700: 'hsl(272 72% 47%)',
          800: 'hsl(273 67% 39%)',
          900: 'hsl(274 66% 32%)',
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        "neural-pulse": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.5 },
        },
        "quantum-glow": {
          "0%, 100%": { 
            boxShadow: "0 0 20px rgba(20, 184, 166, 0.5)",
            transform: "scale(1)"
          },
          "50%": { 
            boxShadow: "0 0 40px rgba(168, 85, 247, 0.8)",
            transform: "scale(1.05)"
          },
        },
        "ai-thinking": {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        "data-flow": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "neural-pulse": "neural-pulse 2s ease-in-out infinite",
        "quantum-glow": "quantum-glow 3s ease-in-out infinite",
        "ai-thinking": "ai-thinking 2s linear infinite",
        "data-flow": "data-flow 2s ease-in-out infinite",
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'neural-pattern': 'linear-gradient(45deg, transparent 25%, rgba(20, 184, 166, 0.1) 25%, rgba(20, 184, 166, 0.1) 50%, transparent 50%, transparent 75%, rgba(168, 85, 247, 0.1) 75%)',
        'grid-pattern': 'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)',
      },
      backgroundSize: {
        'neural': '40px 40px',
        'grid': '20px 20px',
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
}