#!/usr/bin/env python3
"""
RBAC (Role-Based Access Control) Service - Phase C.3
Multi-tenant authorization and permission management
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import jwt
import os

@dataclass
class Tenant:
    id: str
    name: str
    slug: str
    active: bool = True
    settings: Dict = None
    limits: Dict = None

@dataclass
class Role:
    id: str
    name: str
    description: str
    permissions: List[str]
    tenant_id: Optional[str] = None

@dataclass
class UserRole:
    user_id: str
    role_id: str
    tenant_id: str
    granted_at: str
    granted_by: Optional[str] = None

class RBACManager:
    def __init__(self, db_path: str = "rbac.db"):
        self.db_path = db_path
        self.jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-key')
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for fallback"""
        conn = sqlite3.connect(self.db_path)
        
        # Create tables
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                active BOOLEAN DEFAULT 1,
                settings TEXT DEFAULT '{}',
                limits TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                permissions TEXT NOT NULL,
                tenant_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, tenant_id)
            );
            
            CREATE TABLE IF NOT EXISTS user_roles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT,
                UNIQUE(user_id, role_id, tenant_id)
            );
        """)
        
        # Insert default data
        default_tenant_id = "00000000-0000-0000-0000-000000000001"
        conn.execute("""
            INSERT OR IGNORE INTO tenants (id, name, slug) 
            VALUES (?, 'Default Tenant', 'default')
        """, (default_tenant_id,))
        
        # Insert default roles
        default_roles = [
            (str(uuid.uuid4()), 'admin', 'Full administrative access', '["*"]', None),
            (str(uuid.uuid4()), 'operator', 'Operational access', '["workflows:read", "workflows:write", "metrics:read"]', None),
            (str(uuid.uuid4()), 'viewer', 'Read-only access', '["workflows:read", "metrics:read", "reports:read"]', None)
        ]
        
        for role_data in default_roles:
            conn.execute("""
                INSERT OR IGNORE INTO roles (id, name, description, permissions, tenant_id)
                VALUES (?, ?, ?, ?, ?)
            """, role_data)
        
        conn.commit()
        conn.close()
    
    def create_tenant(self, name: str, slug: str, settings: Dict = None, limits: Dict = None) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            settings=settings or {},
            limits=limits or {"max_users": 100, "max_workflows": 1000}
        )
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO tenants (id, name, slug, settings, limits)
            VALUES (?, ?, ?, ?, ?)
        """, (tenant_id, name, slug, json.dumps(tenant.settings), json.dumps(tenant.limits)))
        conn.commit()
        conn.close()
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, name, slug, active, settings, limits
            FROM tenants WHERE id = ?
        """, (tenant_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Tenant(
                id=row[0],
                name=row[1],
                slug=row[2],
                active=bool(row[3]),
                settings=json.loads(row[4] or '{}'),
                limits=json.loads(row[5] or '{}')
            )
        return None
    
    def create_role(self, name: str, description: str, permissions: List[str], tenant_id: str = None) -> Role:
        """Create a new role"""
        role_id = str(uuid.uuid4())
        role = Role(
            id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            tenant_id=tenant_id
        )
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO roles (id, name, description, permissions, tenant_id)
            VALUES (?, ?, ?, ?, ?)
        """, (role_id, name, description, json.dumps(permissions), tenant_id))
        conn.commit()
        conn.close()
        
        return role
    
    def assign_role(self, user_id: str, role_name: str, tenant_id: str, granted_by: str = None) -> UserRole:
        """Assign role to user for specific tenant"""
        # Get role ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id FROM roles 
            WHERE name = ? AND (tenant_id = ? OR tenant_id IS NULL)
            ORDER BY tenant_id NULLS LAST
            LIMIT 1
        """, (role_name, tenant_id))
        
        role_row = cursor.fetchone()
        if not role_row:
            conn.close()
            raise ValueError(f"Role '{role_name}' not found")
        
        role_id = role_row[0]
        assignment_id = str(uuid.uuid4())
        
        # Create assignment
        conn.execute("""
            INSERT OR REPLACE INTO user_roles (id, user_id, role_id, tenant_id, granted_by)
            VALUES (?, ?, ?, ?, ?)
        """, (assignment_id, user_id, role_id, tenant_id, granted_by))
        conn.commit()
        conn.close()
        
        return UserRole(
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            granted_at=datetime.now().isoformat(),
            granted_by=granted_by
        )
    
    def check_permission(self, user_id: str, tenant_id: str, permission: str) -> bool:
        """Check if user has specific permission in tenant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT r.permissions
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = ? AND ur.tenant_id = ?
        """, (user_id, tenant_id))
        
        for row in cursor.fetchall():
            permissions = json.loads(row[0])
            if '*' in permissions or permission in permissions:
                conn.close()
                return True
        
        conn.close()
        return False
    
    def get_user_permissions(self, user_id: str, tenant_id: str) -> Set[str]:
        """Get all permissions for user in tenant"""
        permissions = set()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT r.permissions
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = ? AND ur.tenant_id = ?
        """, (user_id, tenant_id))
        
        for row in cursor.fetchall():
            role_permissions = json.loads(row[0])
            permissions.update(role_permissions)
        
        conn.close()
        return permissions
    
    def get_user_roles(self, user_id: str, tenant_id: str = None) -> List[Dict]:
        """Get user's roles, optionally filtered by tenant"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT ur.tenant_id, t.name as tenant_name, r.name as role_name, 
                   r.description, r.permissions, ur.granted_at
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            JOIN tenants t ON ur.tenant_id = t.id
            WHERE ur.user_id = ?
        """
        params = [user_id]
        
        if tenant_id:
            query += " AND ur.tenant_id = ?"
            params.append(tenant_id)
        
        cursor = conn.execute(query, params)
        
        roles = []
        for row in cursor.fetchall():
            roles.append({
                'tenant_id': row[0],
                'tenant_name': row[1],
                'role_name': row[2],
                'description': row[3],
                'permissions': json.loads(row[4]),
                'granted_at': row[5]
            })
        
        conn.close()
        return roles
    
    def create_jwt_token(self, user_id: str, tenant_id: str, additional_claims: Dict = None) -> str:
        """Create JWT token with tenant and role claims"""
        permissions = list(self.get_user_permissions(user_id, tenant_id))
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'permissions': permissions,
            'iat': int(now.timestamp()),
            'exp': int(now.timestamp()) + 3600  # 1 hour
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def enforce_tenant_isolation(self, user_id: str, tenant_id: str, resource_tenant_id: str) -> bool:
        """Enforce tenant isolation - users can only access their tenant's resources"""
        if tenant_id != resource_tenant_id:
            return False
        
        # Additional check: user must have role in the tenant
        user_roles = self.get_user_roles(user_id, tenant_id)
        return len(user_roles) > 0
    
    def list_tenants(self, active_only: bool = True) -> List[Tenant]:
        """List all tenants"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT id, name, slug, active, settings, limits FROM tenants"
        if active_only:
            query += " WHERE active = 1"
        
        cursor = conn.execute(query)
        
        tenants = []
        for row in cursor.fetchall():
            tenants.append(Tenant(
                id=row[0],
                name=row[1],
                slug=row[2],
                active=bool(row[3]),
                settings=json.loads(row[4] or '{}'),
                limits=json.loads(row[5] or '{}')
            ))
        
        conn.close()
        return tenants

# Decorator for permission checking
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # In a real implementation, this would extract user/tenant from request context
            # For now, we'll pass them as parameters
            user_id = kwargs.get('user_id')
            tenant_id = kwargs.get('tenant_id')
            
            if not user_id or not tenant_id:
                raise ValueError("user_id and tenant_id required")
            
            # Use a shared RBAC instance or pass it in
            rbac_instance = kwargs.get('rbac_instance')
            if not rbac_instance:
                rbac_instance = RBACManager()
            
            if not rbac_instance.check_permission(user_id, tenant_id, permission):
                raise PermissionError(f"Permission '{permission}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage functions
@require_permission('workflows:write')
def create_workflow(user_id: str, tenant_id: str, workflow_data: Dict):
    """Example function requiring workflow write permission"""
    return {"status": "created", "workflow": workflow_data}

@require_permission('metrics:read')
def get_metrics(user_id: str, tenant_id: str):
    """Example function requiring metrics read permission"""
    return {"metrics": "sample_data"}

if __name__ == "__main__":
    # Demo usage
    rbac = RBACManager()
    
    # Create tenant
    tenant = rbac.create_tenant("Acme Corp", "acme-corp")
    print(f"Created tenant: {tenant.name} ({tenant.id})")
    
    # Assign role
    user_id = str(uuid.uuid4())
    assignment = rbac.assign_role(user_id, "operator", tenant.id)
    print(f"Assigned operator role to user {user_id}")
    
    # Check permission
    has_perm = rbac.check_permission(user_id, tenant.id, "workflows:read")
    print(f"User has workflows:read permission: {has_perm}")
    
    # Create JWT
    token = rbac.create_jwt_token(user_id, tenant.id)
    print(f"JWT token created: {token[:50]}...")
    
    # Verify JWT
    payload = rbac.verify_jwt_token(token)
    print(f"JWT verified: {payload['user_id'] if payload else 'Invalid'}")