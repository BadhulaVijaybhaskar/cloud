# Atom Partner TypeScript SDK Documentation

## Installation
```bash
npm install @atom/partner-sdk
```

## Usage
```typescript
import { AtomPartnerClient } from '@atom/partner-sdk';

const client = new AtomPartnerClient('http://localhost:8200');
await client.registerPartner({
  name: 'My Company',
  email: 'contact@company.com',
  org: 'Company Inc'
});
```

## API Reference
- `registerPartner(payload)` - Register a new partner
- `getPartner(id)` - Get partner details
- `publishPackage(data)` - Publish package to marketplace
