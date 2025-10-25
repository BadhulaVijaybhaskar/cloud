#!/usr/bin/env python3
"""
Test script for tenant isolation and RLS policies.
Simulates cross-tenant access attempts to verify security.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenancyTester:
    """Test tenant isolation and RLS policies."""
    
    def __init__(self, db_dsn: Optional[str] = None):
        self.db_dsn = db_dsn or os.getenv("POSTGRES_DSN")
        if not self.db_dsn:
            raise ValueError("POSTGRES_DSN environment variable required")
    
    def test_cross_tenant_access(self) -> Dict[str, Any]:
        """Test cross-tenant access scenarios."""
        results = {
            "test_name": "cross_tenant_access",
            "status": "unknown",
            "tests": [],
            "summary": {}
        }
        
        try:
            with psycopg2.connect(self.db_dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    
                    # Test 1: Create test tenants and data
                    tenant1_id = "11111111-1111-1111-1111-111111111111"
                    tenant2_id = "22222222-2222-2222-2222-222222222222"
                    
                    # Setup test data
                    self._setup_test_data(cur, tenant1_id, tenant2_id)
                    
                    # Test 2: Verify tenant1 can only see its own data
                    test1_result = self._test_tenant_isolation(cur, tenant1_id, "tenant1")
                    results["tests"].append(test1_result)
                    
                    # Test 3: Verify tenant2 can only see its own data  
                    test2_result = self._test_tenant_isolation(cur, tenant2_id, "tenant2")
                    results["tests"].append(test2_result)
                    
                    # Test 4: Attempt cross-tenant access (should fail)
                    test3_result = self._test_cross_tenant_violation(cur, tenant1_id, tenant2_id)
                    results["tests"].append(test3_result)
                    
                    # Cleanup
                    self._cleanup_test_data(cur, tenant1_id, tenant2_id)
                    
                    conn.commit()
                    
            # Determine overall status
            passed_tests = sum(1 for test in results["tests"] if test["passed"])
            total_tests = len(results["tests"])
            
            results["summary"] = {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            }
            
            results["status"] = "PASS" if passed_tests == total_tests else "FAIL"
            
        except psycopg2.Error as e:
            logger.error(f"Database error during tenancy test: {e}")
            results["status"] = "BLOCKED"
            results["error"] = str(e)
        except Exception as e:
            logger.error(f"Unexpected error during tenancy test: {e}")
            results["status"] = "BLOCKED" 
            results["error"] = str(e)
        
        return results
    
    def _setup_test_data(self, cur, tenant1_id: str, tenant2_id: str):
        """Setup test data for tenancy testing."""
        
        # Create test workflow runs for each tenant
        cur.execute("""
            INSERT INTO workflow_runs (id, tenant_id, workflow_name, status, created_at)
            VALUES 
                ('run1-tenant1', %s, 'test-workflow-1', 'completed', NOW()),
                ('run2-tenant1', %s, 'test-workflow-2', 'running', NOW()),
                ('run1-tenant2', %s, 'test-workflow-1', 'completed', NOW()),
                ('run2-tenant2', %s, 'test-workflow-3', 'failed', NOW())
            ON CONFLICT (id) DO NOTHING
        """, (tenant1_id, tenant1_id, tenant2_id, tenant2_id))
        
        logger.info("Test data created for tenancy testing")
    
    def _test_tenant_isolation(self, cur, tenant_id: str, tenant_name: str) -> Dict[str, Any]:
        """Test that a tenant can only see its own data."""
        
        test_result = {
            "test_name": f"tenant_isolation_{tenant_name}",
            "tenant_id": tenant_id,
            "passed": False,
            "details": {}
        }
        
        try:
            # Set tenant context
            cur.execute("SET app.current_tenant = %s", (tenant_id,))
            
            # Query workflow runs (should only see own tenant's data)
            cur.execute("SELECT id, tenant_id, workflow_name FROM workflow_runs")
            rows = cur.fetchall()
            
            # Verify all returned rows belong to current tenant
            own_tenant_rows = [row for row in rows if row['tenant_id'] == tenant_id]
            other_tenant_rows = [row for row in rows if row['tenant_id'] != tenant_id]
            
            test_result["details"] = {
                "total_rows": len(rows),
                "own_tenant_rows": len(own_tenant_rows),
                "other_tenant_rows": len(other_tenant_rows),
                "expected_own_rows": 2  # We inserted 2 rows per tenant
            }
            
            # Test passes if:
            # 1. We see exactly our own tenant's rows
            # 2. We see no other tenant's rows
            test_result["passed"] = (
                len(own_tenant_rows) == 2 and 
                len(other_tenant_rows) == 0
            )
            
            if test_result["passed"]:
                logger.info(f"✅ {tenant_name} isolation test passed")
            else:
                logger.error(f"❌ {tenant_name} isolation test failed: saw {len(other_tenant_rows)} other tenant rows")
                
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"Error in tenant isolation test for {tenant_name}: {e}")
        
        return test_result
    
    def _test_cross_tenant_violation(self, cur, tenant1_id: str, tenant2_id: str) -> Dict[str, Any]:
        """Test that cross-tenant access is properly blocked."""
        
        test_result = {
            "test_name": "cross_tenant_violation",
            "passed": False,
            "details": {}
        }
        
        try:
            # Set context to tenant1
            cur.execute("SET app.current_tenant = %s", (tenant1_id,))
            
            # Try to access tenant2's specific data (should be blocked by RLS)
            cur.execute("""
                SELECT id, tenant_id, workflow_name 
                FROM workflow_runs 
                WHERE tenant_id = %s
            """, (tenant2_id,))
            
            rows = cur.fetchall()
            
            test_result["details"] = {
                "attempted_tenant": tenant2_id,
                "current_tenant": tenant1_id,
                "rows_returned": len(rows),
                "expected_rows": 0  # Should be 0 due to RLS
            }
            
            # Test passes if no rows are returned (RLS blocks access)
            test_result["passed"] = len(rows) == 0
            
            if test_result["passed"]:
                logger.info("✅ Cross-tenant access properly blocked")
            else:
                logger.error(f"❌ Cross-tenant access violation: returned {len(rows)} rows")
                
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"Error in cross-tenant violation test: {e}")
        
        return test_result
    
    def _cleanup_test_data(self, cur, tenant1_id: str, tenant2_id: str):
        """Clean up test data."""
        cur.execute("""
            DELETE FROM workflow_runs 
            WHERE id IN ('run1-tenant1', 'run2-tenant1', 'run1-tenant2', 'run2-tenant2')
        """)
        logger.info("Test data cleaned up")

def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test tenant isolation and RLS policies")
    parser.add_argument("--simulate-cross-tenant", action="store_true", 
                       help="Simulate cross-tenant access attempts")
    parser.add_argument("--output", default="json", choices=["json", "text"],
                       help="Output format")
    
    args = parser.parse_args()
    
    try:
        tester = TenancyTester()
        
        if args.simulate_cross_tenant:
            results = tester.test_cross_tenant_access()
            
            if args.output == "json":
                print(json.dumps(results, indent=2))
            else:
                print(f"Tenancy Test Results: {results['status']}")
                print(f"Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
                for test in results["tests"]:
                    status = "✅ PASS" if test["passed"] else "❌ FAIL"
                    print(f"  {test['test_name']}: {status}")
        
    except Exception as e:
        error_result = {
            "status": "BLOCKED",
            "error": str(e),
            "message": "Could not connect to database or RLS not configured"
        }
        
        if args.output == "json":
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Tenancy test blocked: {e}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()