# NeuralOps UI API Documentation

## Overview
The NeuralOps UI is a Next.js application that provides a web interface for incident management, playbook execution, and cluster onboarding.

## Architecture

### Frontend Stack
- **Framework**: Next.js 14 with React 18
- **Styling**: Custom CSS with responsive design
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Fetch API with fallback handling

### API Proxy
- **Server**: Express.js proxy server on port 8080
- **Purpose**: CORS handling and JWT injection for development
- **Fallback**: Mock endpoints when backend services unavailable

## API Endpoints

### Backend Services Integration
```
/api/orchestrator/*  → http://localhost:8004
/api/recommender/*   → http://localhost:8003  
/api/insights/*      → http://localhost:8002
/api/registry/*      → http://localhost:8000
/api/runtime/*       → http://localhost:8001
```

### Mock Endpoints (Development)
```
GET /api/mock/incidents     - Sample incident data
GET /api/mock/playbooks     - Sample playbook catalog
```

## Development Setup

### Prerequisites
```bash
Node.js 18+
npm or yarn
```

### Installation
```bash
cd ui/neuralops
npm install
```

### Development Server
```bash
# Start UI (port 3001)
npm run dev

# Start API proxy (port 8080) 
npm run proxy
```

## Testing

### Smoke Tests
```bash
node tests/ui_smoke.test.js
```

## Deployment

### Production Build
```bash
npm run build
npm start
```