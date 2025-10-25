#!/usr/bin/env python3
"""
Tests for NeuralOps Recommender API
"""

import pytest
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import RecommenderEngine, RecommendRequest

class TestRecommenderEngine:
    """Test cases for RecommenderEngine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.engine = RecommenderEngine()
    
    def test_load_playbooks(self):
        """Test playbook loading."""
        playbooks = self.engine._load_playbooks()
        
        assert len(playbooks) > 0
        assert all("id" in pb for pb in playbooks)
        assert all("name" in pb for pb in playbooks)
        assert all("success_rate" in pb for pb in playbooks)
    
    def test_rule_based_recommendations_backup(self):
        """Test rule-based recommendations for backup incident."""
        context = {
            "description": "backup verification failed",
            "labels": {"service": "backup"},
            "signal_data": None
        }
        
        recommendations = self.engine._rule_based_recommendations(context, 5)
        
        assert len(recommendations) > 0
        # Should recommend backup-related playbook
        backup_rec = next((r for r in recommendations if "backup" in r.playbook_id), None)
        assert backup_rec is not None
        assert backup_rec.score > 0.1
    
    def test_calculate_similarity_score(self):
        """Test similarity score calculation."""
        playbook = {
            "name": "Backup Verification",
            "description": "Verify backup integrity",
            "tags": ["backup", "verification"]
        }
        
        # High similarity
        score1 = self.engine._calculate_similarity_score("backup verification failed", playbook)
        assert score1 > 0.1
        
        # No similarity
        score2 = self.engine._calculate_similarity_score("", playbook)
        assert score2 == 0.0
    
    def test_recommend_basic(self):
        """Test basic recommendation generation."""
        request = RecommendRequest(
            incident_description="backup process failed",
            labels={"component": "backup"},
            limit=3
        )
        
        response = self.engine.recommend(request)
        
        assert len(response.recommendations) <= 3
        assert response.total_candidates == len(self.engine.playbooks)
        assert response.method in ["vector_similarity", "rule_based"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])