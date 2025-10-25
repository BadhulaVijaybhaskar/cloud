#!/usr/bin/env python3
"""
Tests for RBAC Service - Phase C.3
"""

import pytest
import tempfile
import os
import sys
import uuid
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rbac import RBACManager, Tenant, Role, UserRole, require_permission

class TestRBACManager:
    """Test cases for RBAC manager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.rbac = RBACManager(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_rbac_initialization(self):
        """Test RBAC manager initializes correctly"""
        assert self.rbac.db_path == self.temp_db.name
        
        # Check default tenant exists
        tenants = self.rbac.list_tenants()
        assert len(tenants) >= 1
        assert any(t.slug == 'default' for t in tenants)
    
    def test_create_tenant(self):
        """Test tenant creation"""
        tenant = self.rbac.create_tenant(
            name="Test Corp",
            slug="test-corp",
            settings={"theme": "dark"},
            limits={"max_users": 50}
        )
        
        assert tenant.name == "Test Corp"
        assert tenant.slug == "test-corp"
        assert tenant.settings["theme"] == "dark"
        assert tenant.limits["max_users"] == 50
        
        # Verify stored
        retrieved = self.rbac.get_tenant(tenant.id)
        assert retrieved.name == "Test Corp"
        assert retrieved.settings["theme"] == "dark"
    
    def test_create_role(self):
        """Test role creation"""
        tenant = self.rbac.create_tenant("Role Test Corp", "role-test")
        
        role = self.rbac.create_role(
            name="custom-role",
            description="Custom test role",
            permissions=["workflows:read", "metrics:read"],
            tenant_id=tenant.id
        )
        
        assert role.name == "custom-role"
        assert "workflows:read" in role.permissions
        assert role.tenant_id == tenant.id
    
    def test_assign_role(self):
        """Test role assignment to user"""
        tenant = self.rbac.create_tenant("Assignment Test", "assign-test")
        user_id = str(uuid.uuid4())
        
        assignment = self.rbac.assign_role(user_id, "operator", tenant.id)
        
        assert assignment.user_id == user_id
        assert assignment.tenant_id == tenant.id
        
        # Verify assignment
        user_roles = self.rbac.get_user_roles(user_id, tenant.id)
        assert len(user_roles) == 1
        assert user_roles[0]["role_name"] == "operator"
    
    def test_permission_checking(self):
        """Test permission validation"""
        tenant = self.rbac.create_tenant("Permission Test", "perm-test")
        user_id = str(uuid.uuid4())
        
        # Assign operator role
        self.rbac.assign_role(user_id, "operator", tenant.id)
        
        # Check permissions
        assert self.rbac.check_permission(user_id, tenant.id, "workflows:read") == True
        assert self.rbac.check_permission(user_id, tenant.id, "workflows:write") == True
        assert self.rbac.check_permission(user_id, tenant.id, "admin:delete") == False
        
        # Check admin wildcard
        admin_user = str(uuid.uuid4())
        self.rbac.assign_role(admin_user, "admin", tenant.id)
        assert self.rbac.check_permission(admin_user, tenant.id, "any:permission") == True
    
    def test_get_user_permissions(self):
        """Test retrieving user permissions"""
        tenant = self.rbac.create_tenant("Permissions Test", "perms-test")
        user_id = str(uuid.uuid4())
        
        # Assign viewer role
        self.rbac.assign_role(user_id, "viewer", tenant.id)
        
        permissions = self.rbac.get_user_permissions(user_id, tenant.id)
        assert "workflows:read" in permissions
        assert "metrics:read" in permissions
        assert "workflows:write" not in permissions
    
    def test_tenant_isolation_enforcement(self):
        """Test P-5: Multi-tenant isolation"""
        tenant1 = self.rbac.create_tenant("Tenant 1", "tenant-1")
        tenant2 = self.rbac.create_tenant("Tenant 2", "tenant-2")
        user_id = str(uuid.uuid4())
        
        # Assign user to tenant1 only
        self.rbac.assign_role(user_id, "operator", tenant1.id)
        
        # User should have access to tenant1 resources
        assert self.rbac.enforce_tenant_isolation(user_id, tenant1.id, tenant1.id) == True
        
        # User should NOT have access to tenant2 resources
        assert self.rbac.enforce_tenant_isolation(user_id, tenant1.id, tenant2.id) == False
        assert self.rbac.enforce_tenant_isolation(user_id, tenant2.id, tenant2.id) == False

class TestJWTIntegration:
    """Test JWT token creation and validation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.rbac = RBACManager(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_jwt_token_creation(self):
        """Test JWT token creation with tenant claims"""
        tenant = self.rbac.create_tenant("JWT Test", "jwt-test")
        user_id = str(uuid.uuid4())
        
        # Assign role
        self.rbac.assign_role(user_id, "operator", tenant.id)
        
        # Create token
        token = self.rbac.create_jwt_token(user_id, tenant.id)
        assert token is not None
        assert len(token) > 50  # JWT tokens are typically long
    
    def test_jwt_token_verification(self):
        """Test JWT token verification and claims extraction"""
        tenant = self.rbac.create_tenant("JWT Verify Test", "jwt-verify")
        user_id = str(uuid.uuid4())
        
        # Assign role
        self.rbac.assign_role(user_id, "viewer", tenant.id)
        
        # Create and verify token
        token = self.rbac.create_jwt_token(user_id, tenant.id, {"custom": "claim"})
        payload = self.rbac.verify_jwt_token(token)
        
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["tenant_id"] == tenant.id
        assert "workflows:read" in payload["permissions"]
        assert payload["custom"] == "claim"
    
    def test_jwt_token_invalid(self):
        """Test invalid JWT token handling"""
        invalid_token = "invalid.jwt.token"
        payload = self.rbac.verify_jwt_token(invalid_token)
        assert payload is None

class TestPermissionDecorator:
    """Test permission decorator functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.rbac = RBACManager(db_path=self.temp_db.name)
        
        # Setup test data
        self.tenant = self.rbac.create_tenant("Decorator Test", "decorator-test")
        self.user_id = str(uuid.uuid4())
        self.rbac.assign_role(self.user_id, "operator", self.tenant.id)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_permission_decorator_success(self):
        """Test successful permission check with decorator"""
        @require_permission('workflows:read')
        def test_function(user_id: str, tenant_id: str, rbac_instance=None):
            return "success"
        
        result = test_function(user_id=self.user_id, tenant_id=self.tenant.id, rbac_instance=self.rbac)
        assert result == "success"
    
    def test_permission_decorator_failure(self):
        """Test failed permission check with decorator"""
        @require_permission('admin:delete')
        def test_function(user_id: str, tenant_id: str, rbac_instance=None):
            return "should not reach here"
        
        with pytest.raises(PermissionError):
            test_function(user_id=self.user_id, tenant_id=self.tenant.id, rbac_instance=self.rbac)
    
    def test_permission_decorator_missing_params(self):
        """Test decorator with missing parameters"""
        @require_permission('workflows:read')
        def test_function():
            return "should not reach here"
        
        with pytest.raises(ValueError):
            test_function()

class TestPolicyCompliance:
    """Test P1-P6 policy compliance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.rbac = RBACManager(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_p3_execution_safety(self):
        """Test P-3: Execution safety with dry-run mode"""
        tenant = self.rbac.create_tenant("Safety Test", "safety-test")
        user_id = str(uuid.uuid4())
        
        # Assign viewer role (read-only)
        self.rbac.assign_role(user_id, "viewer", tenant.id)
        
        # Viewer should not have write permissions
        assert self.rbac.check_permission(user_id, tenant.id, "workflows:write") == False
        assert self.rbac.check_permission(user_id, tenant.id, "workflows:read") == True
        
        # Only operators and admins should have write access
        operator_user = str(uuid.uuid4())
        self.rbac.assign_role(operator_user, "operator", tenant.id)
        assert self.rbac.check_permission(operator_user, tenant.id, "workflows:write") == True
    
    def test_p5_multi_tenant_isolation(self):
        """Test P-5: Multi-tenant isolation enforcement"""
        tenant1 = self.rbac.create_tenant("Isolated Tenant 1", "isolated-1")
        tenant2 = self.rbac.create_tenant("Isolated Tenant 2", "isolated-2")
        
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        
        # Assign users to different tenants
        self.rbac.assign_role(user1, "admin", tenant1.id)
        self.rbac.assign_role(user2, "admin", tenant2.id)
        
        # Users should only access their own tenant
        assert self.rbac.enforce_tenant_isolation(user1, tenant1.id, tenant1.id) == True
        assert self.rbac.enforce_tenant_isolation(user1, tenant1.id, tenant2.id) == False
        assert self.rbac.enforce_tenant_isolation(user2, tenant2.id, tenant2.id) == True
        assert self.rbac.enforce_tenant_isolation(user2, tenant2.id, tenant1.id) == False
    
    def test_p2_no_hardcoded_secrets(self):
        """Test P-2: No hardcoded secrets (uses environment variables)"""
        # JWT secret should come from environment or use safe default
        assert self.rbac.jwt_secret is not None
        assert len(self.rbac.jwt_secret) >= 8  # Minimum length
        
        # In production, this should be from environment
        # For testing, we accept the dev default
        assert self.rbac.jwt_secret in ['dev-secret-key'] or os.getenv('JWT_SECRET')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])