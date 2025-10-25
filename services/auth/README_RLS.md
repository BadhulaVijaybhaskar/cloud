# Auth Service RLS Integration

## JWT to Tenant Mapping
```javascript
// Extract tenant from JWT
const token = jwt.verify(authHeader, secret);
const tenantId = token.tenant || 'default';

// Set database context
await db.query('SET app.current_tenant = $1', [tenantId]);
```

## Middleware Implementation
```javascript
app.use((req, res, next) => {
  const tenant = extractTenantFromJWT(req.headers.authorization);
  req.tenant = tenant;
  next();
});
```

## Database Connection
Each request sets tenant context before executing queries to ensure RLS enforcement.