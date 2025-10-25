#!/usr/bin/env python3
"""
Tests for NeuralOps Incident Orchestrator
"""

import pytest
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import OrchestrationEngine, OrchestrationRequest, ApprovalRequest

class TestOrchestrationEngine:
    """Test cases for OrchestrationEngine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.engine = OrchestrationEngine()
        self.engine.db_path = ":memory:"
        self.engine._init_db()
    
    def test_suggest_workflow(self):
        """Test suggest stage of orchestration."""
        request = OrchestrationRequest(
            playbook_id="backup-verify",
            incident_description="backup failure detected",
            labels={"service": "backup"}
        )
        
        with patch.object(self.engine, '_get_recommendations') as mock_rec:
            mock_rec.return_value = [{
                "playbook_id": "backup-verify",
                "score": 0.9,
                "justification": "High confidence match"
            }]
            
            response = self.engine.suggest(request)
            
            assert response.stage == "suggest"
            assert response.status == "pending"
            assert response.playbook_id == "backup-verify"
            assert len(response.recommendations) == 1
    
    def test_dry_run_workflow(self):
        """Test dry-run stage of orchestration."""
        # First create orchestration
        request = OrchestrationRequest(playbook_id="backup-verify")
        
        with patch.object(self.engine, '_get_recommendations', return_value=[]):
            suggest_response = self.engine.suggest(request)
        
        # Then test dry-run
        with patch.object(self.engine, '_call_registry_dry_run') as mock_dry:
            mock_dry.return_value = {"valid": True, "method": "test"}
            
            dry_run_response = self.engine.dry_run(suggest_response.orchestration_id)
            
            assert dry_run_response.stage == "dry_run"
            assert dry_run_response.status == "completed"
            assert dry_run_response.dry_run_result is not None
    
    def test_validate_approver(self):
        """Test approver validation."""
        # Valid token
        result = self.engine._validate_approver("Bearer admin-token")
        assert result["user_id"] == "admin"
        
        # Invalid token
        with pytest.raises(Exception):
            self.engine._validate_approver("invalid-token")
    
    def test_fallback_recommendations(self):
        """Test fallback when recommender unavailable."""
        request = OrchestrationRequest(playbook_id="backup-verify")
        
        with patch('requests.post', side_effect=Exception("Service unavailable")):
            recommendations = self.engine._get_recommendations(request)
            
            assert len(recommendations) == 1
            assert recommendations[0]["playbook_id"] == "backup-verify"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])