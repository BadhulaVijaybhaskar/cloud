# ATOM Admin Console

Professional-grade admin dashboard for ATOM Cloud infrastructure management.

## Features

- **Multi-tenant Management**: Comprehensive tenant oversight and administration
- **Real-time Monitoring**: Live system metrics and performance tracking
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Theme Support**: Light/Dark/Auto theme switching
- **ATOM Branding**: Consistent design system with gradient branding
- **Accessibility**: WCAG 2.1 AA compliant interface

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Development

The ATOM Admin Console is built with:

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Consistent iconography
- **ATOM Design System**: Custom theme tokens and components

## Project Structure

```
src/
├── components/
│   ├── Layout/
│   │   ├── AtomSidebar.tsx
│   │   ├── AtomTopbar.tsx
│   │   ├── AtomFooter.tsx
│   │   └── AtomLayout.tsx
│   ├── AtomCard.tsx
│   ├── AtomButton.tsx
│   └── AtomThemeChooser.tsx
├── pages/
│   ├── atom/
│   │   ├── dashboard.tsx
│   │   └── tenants/
│   └── _app.tsx
├── styles/
│   ├── theme.css
│   └── globals.css
└── utils/
```

## ATOM Theme System

The admin console uses a comprehensive theme system with:

- **CSS Custom Properties**: Dynamic theme switching
- **Semantic Color Tokens**: Consistent color usage
- **ATOM Gradient Branding**: Primary brand colors
- **Component Utilities**: Reusable styling classes

## Available Scripts

- `npm run dev` - Start development server on port 3001
- `npm run build` - Build production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Environment Variables

```bash
ATOM_APP_NAME=ATOM Admin Console
ATOM_VERSION=1.0.0
```

## Contributing

1. Follow ATOM naming conventions
2. Use TypeScript for all components
3. Maintain accessibility standards
4. Test responsive design on multiple devices
5. Ensure theme compatibility (light/dark)

## License

MIT License - ATOM Cloud Team